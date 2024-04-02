import json
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Union, Optional, Dict, List, Sequence

from core.callbacks.base import BaseCallbackHandler
from core.callbacks.utils import (
    BaseMetadataCallbackHandler,
    flatten_dict,
    hash_string,
    import_pandas,
    import_spacy,
    import_textstat,
)


def import_wandb() -> Any:
    """Import the wandb python package and raise an error if it is not installed."""
    try:
        import wandb  # noqa: F401
    except ImportError:
        raise ImportError(
            "To use the wandb callback manager you need to have the `wandb` python "
            "package installed. Please install it with `pip install wandb`"
        )
    return wandb


def load_json_to_dict(json_path: Union[str, Path]) -> dict:
    """Load json file to a dictionary.

    Parameters:
        json_path (str): The path to the json file.

    Returns:
        (dict): The dictionary representation of the json file.
    """
    with open(json_path, "r") as f:
        data = json.load(f)
    return data


def analyze_text(
    text: str,
    complexity_metrics: bool = True,
    visualize: bool = True,
    nlp: Any = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> dict:
    """Analyze text using textstat and spacy.

    Parameters:
        text (str): The text to analyze.
        complexity_metrics (bool): Whether to compute complexity metrics.
        visualize (bool): Whether to visualize the text.
        nlp (spacy.lang): The spacy language model to use for visualization.
        output_dir (str): The directory to save the visualization files to.

    Returns:
        (dict): A dictionary containing the complexity metrics and visualization
            files serialized in a wandb.Html element.
    """
    resp = {}
    textstat = import_textstat()
    wandb = import_wandb()
    spacy = import_spacy()
    if complexity_metrics:
        text_complexity_metrics = {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "smog_index": textstat.smog_index(text),
            "coleman_liau_index": textstat.coleman_liau_index(text),
            "automated_readability_index": textstat.automated_readability_index(text),
            "dale_chall_readability_score": textstat.dale_chall_readability_score(text),
            "difficult_words": textstat.difficult_words(text),
            "linsear_write_formula": textstat.linsear_write_formula(text),
            "gunning_fog": textstat.gunning_fog(text),
            "text_standard": textstat.text_standard(text),
            "fernandez_huerta": textstat.fernandez_huerta(text),
            "szigriszt_pazos": textstat.szigriszt_pazos(text),
            "gutierrez_polini": textstat.gutierrez_polini(text),
            "crawford": textstat.crawford(text),
            "gulpease_index": textstat.gulpease_index(text),
            "osman": textstat.osman(text),
        }
        resp.update(text_complexity_metrics)

    if visualize and nlp and output_dir is not None:
        doc = nlp(text)

        dep_out = spacy.displacy.render(doc, style="dep", jupyter=False, page=True)
        dep_output_path = Path(output_dir, hash_string(f"dep-{text}") + ".html")
        dep_output_path.open("w", encoding="utf-8").write(dep_out)

        ent_out = spacy.displacy.render(doc, style="ent", jupyter=False, page=True)
        ent_output_path = Path(output_dir, hash_string(f"ent-{text}") + ".html")
        ent_output_path.open("w", encoding="utf-8").write(ent_out)

        text_visualizations = {
            "dependency_tree": wandb.Html(str(dep_output_path)),
            "entities": wandb.Html(str(ent_output_path)),
        }
        resp.update(text_visualizations)

    return resp


def construct_html_from_prompt_and_generation(prompt: str, generation: str) -> Any:
    """Construct an html element from a prompt and a generation.

    Parameters:
        prompt (str): The prompt.
        generation (str): The generation.

    Returns:
        (wandb.Html): The html element."""
    wandb = import_wandb()
    formatted_prompt = prompt.replace("\n", "<br>")
    formatted_generation = generation.replace("\n", "<br>")

    return wandb.Html(
        f"""
    <p style="color:black;">{formatted_prompt}:</p>
    <blockquote>
      <p style="color:green;">
        {formatted_generation}
      </p>
    </blockquote>
    """,
        inject=False,
    )


class WandbCallbackHandler(BaseMetadataCallbackHandler, BaseCallbackHandler):
    """Callback Handler that logs to Weights and Biases.

    Parameters:
        job_type (str): The type of job.
        project (str): The project to log to.
        entity (str): The entity to log to.
        tags (list): The tags to log.
        group (str): The group to log to.
        name (str): The name of the run.
        notes (str): The notes to log.
        visualize (bool): Whether to visualize the run.
        complexity_metrics (bool): Whether to log complexity metrics.
        stream_logs (bool): Whether to stream callback actions to W&B

    This handler will utilize the associated callback method called and formats
    the input of each callback function with metadata regarding the state of LLM run,
    and adds the response to the list of records for both the {method}_records and
    action. It then logs the response using the run.log() method to Weights and Biases.
    """

    def __init__(
        self,
        job_type: Optional[str] = None,
        project: Optional[str] = "langchain_callback_demo",
        entity: Optional[str] = None,
        tags: Optional[Sequence] = None,
        group: Optional[str] = None,
        name: Optional[str] = None,
        notes: Optional[str] = None,
        visualize: bool = False,
        complexity_metrics: bool = False,
        stream_logs: bool = False,
    ) -> None:
        """Initialize callback handler."""

        wandb = import_wandb()
        import_pandas()
        import_textstat()
        spacy = import_spacy()
        super().__init__()

        self.job_type = job_type
        self.project = project
        self.entity = entity
        self.tags = tags
        self.group = group
        self.name = name
        self.notes = notes
        self.visualize = visualize
        self.complexity_metrics = complexity_metrics
        self.stream_logs = stream_logs

        self.temp_dir = tempfile.TemporaryDirectory()
        self.run = wandb.init(
            job_type=self.job_type,
            project=self.project,
            entity=self.entity,
            tags=self.tags,
            group=self.group,
            name=self.name,
            notes=self.notes,
        )
        warning = (
            "DEPRECATION: The `WandbCallbackHandler` will soon be deprecated in favor "
            "of the `WandbTracer`. Please update your code to use the `WandbTracer` "
            "instead."
        )
        wandb.termwarn(
            warning,
            repeat=False,
        )
        self.callback_columns: list = []
        self.action_records: list = []
        self.complexity_metrics = complexity_metrics
        self.visualize = visualize
        self.nlp = spacy.load("en_core_web_sm")

    def _init_resp(self) -> Dict:
        return {k: None for k in self.callback_columns}

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts."""
        self.step += 1
        self.llm_starts += 1
        self.starts += 1

        resp = self._init_resp()
        resp.update({"action": "on_llm_start"})
        resp.update(flatten_dict(serialized))
        resp.update(self.get_custom_callback_meta())

        for prompt in prompts:
            prompt_resp = deepcopy(resp)
            prompt_resp["prompts"] = prompt
            self.on_llm_start_records.append(prompt_resp)
            self.action_records.append(prompt_resp)
            if self.stream_logs:
                self.run.log(prompt_resp)
