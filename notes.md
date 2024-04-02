## Notes
- @root_validator is used to initialize the client in Model.
- At least one of the base class should be inheriting BaseModel so that the class can initialize using x=y key values in constructor. 
- lang-serve and lang-core connection
  - lang-serve client.py
    - self._call_with_config(self._invoke, input, config=config)
    - https://github.com/langchain-ai/langserve/blob/main/langserve/client.py#L355
  - lang-core Runnable
    - https://github.com/langchain-ai/langchain/blob/ed49cca1919c71fa51256346a51a5316196173c7/libs/core/langchain_core/runnables/base.py#L1596
  - 