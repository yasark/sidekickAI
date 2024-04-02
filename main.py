from core.language_models.base import BaseLanguageModel
from core.language_models.model import SideKick


def run():

    model = SideKick()
    model.invoke("")

if __name__ == '__main__':
    run()