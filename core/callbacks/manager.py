# from typing import List, Optional, Any
#
# from core.callbacks.base import BaseCallbackManager, BaseCallbackHandler
#
#
# def handle_event(
#         handlers: List[BaseCallbackHandler],
#         event_name: str,
#         ignore_condition_name: Optional[str],
#         *args: Any,
#         **kwargs: Any,
# ) -> None:
#     """Generic event handler for CallbackManager.
#
#     Note: This function is used by langserve to handle events.
#
#     Args:
#         handlers: The list of handlers that will handle the event
#         event_name: The name of the event (e.g., "on_llm_start")
#         ignore_condition_name: Name of the attribute defined on handler
#             that if True will cause the handler to be skipped for the given event
#         *args: The arguments to pass to the event handler
#         **kwargs: The keyword arguments to pass to the event handler
#     """
#     coros: List[Coroutine[Any, Any, Any]] = []
#
#     try:
#         message_strings: Optional[List[str]] = None
#         for handler in handlers:
#             try:
#                 if ignore_condition_name is None or not getattr(
#                         handler, ignore_condition_name
#                 ):
#                     event = getattr(handler, event_name)(*args, **kwargs)
#                     if asyncio.iscoroutine(event):
#                         coros.append(event)
#             except NotImplementedError as e:
#                 if event_name == "on_chat_model_start":
#                     if message_strings is None:
#                         message_strings = [get_buffer_string(m) for m in args[1]]
#                     handle_event(
#                         [handler],
#                         "on_llm_start",
#                         "ignore_llm",
#                         args[0],
#                         message_strings,
#                         *args[2:],
#                         **kwargs,
#                     )
#                 else:
#                     handler_name = handler.__class__.__name__
#                     logger.warning(
#                         f"NotImplementedError in {handler_name}.{event_name}"
#                         f" callback: {repr(e)}"
#                     )
#             except Exception as e:
#                 logger.warning(
#                     f"Error in {handler.__class__.__name__}.{event_name} callback:"
#                     f" {repr(e)}"
#                 )
#                 if handler.raise_error:
#                     raise e
#     finally:
#         if coros:
#             try:
#                 # Raises RuntimeError if there is no current event loop.
#                 asyncio.get_running_loop()
#                 loop_running = True
#             except RuntimeError:
#                 loop_running = False
#
#             if loop_running:
#                 # If we try to submit this coroutine to the running loop
#                 # we end up in a deadlock, as we'd have gotten here from a
#                 # running coroutine, which we cannot interrupt to run this one.
#                 # The solution is to create a new loop in a new thread.
#                 with ThreadPoolExecutor(1) as executor:
#                     executor.submit(
#                         cast(Callable, copy_context().run), _run_coros, coros
#                     ).result()
#             else:
#                 _run_coros(coros)
#
#
# def _run_coros(coros: List[Coroutine[Any, Any, Any]]) -> None:
#     if hasattr(asyncio, "Runner"):
#         # Python 3.11+
#         # Run the coroutines in a new event loop, taking care to
#         # - install signal handlers
#         # - run pending tasks scheduled by `coros`
#         # - close asyncgens and executors
#         # - close the loop
#         with asyncio.Runner() as runner:
#             # Run the coroutine, get the result
#             for coro in coros:
#                 try:
#                     runner.run(coro)
#                 except Exception as e:
#                     logger.warning(f"Error in callback coroutine: {repr(e)}")
#
#             # Run pending tasks scheduled by coros until they are all done
#             while pending := asyncio.all_tasks(runner.get_loop()):
#                 runner.run(asyncio.wait(pending))
#     else:
#         # Before Python 3.11 we need to run each coroutine in a new event loop
#         # as the Runner api is not available.
#         for coro in coros:
#             try:
#                 asyncio.run(coro)
#             except Exception as e:
#                 logger.warning(f"Error in callback coroutine: {repr(e)}")
#
#
# class CallbackManager(BaseCallbackManager):
#     """Callback manager that handles callbacks from LangChain."""
#
#     def on_llm_start(
#             self,
#             serialized: Dict[str, Any],
#             prompts: List[str],
#             run_id: Optional[UUID] = None,
#             **kwargs: Any,
#     ) -> List[CallbackManagerForLLMRun]:
#         """Run when LLM starts running.
#
#         Args:
#             serialized (Dict[str, Any]): The serialized LLM.
#             prompts (List[str]): The list of prompts.
#             run_id (UUID, optional): The ID of the run. Defaults to None.
#
#         Returns:
#             List[CallbackManagerForLLMRun]: A callback manager for each
#                 prompt as an LLM run.
#         """
#         managers = []
#         for i, prompt in enumerate(prompts):
#             # Can't have duplicate runs with the same run ID (if provided)
#             run_id_ = run_id if i == 0 and run_id is not None else uuid.uuid4()
#             handle_event(
#                 self.handlers,
#                 "on_llm_start",
#                 "ignore_llm",
#                 serialized,
#                 [prompt],
#                 run_id=run_id_,
#                 parent_run_id=self.parent_run_id,
#                 tags=self.tags,
#                 metadata=self.metadata,
#                 **kwargs,
#             )
#
#             managers.append(
#                 CallbackManagerForLLMRun(
#                     run_id=run_id_,
#                     handlers=self.handlers,
#                     inheritable_handlers=self.inheritable_handlers,
#                     parent_run_id=self.parent_run_id,
#                     tags=self.tags,
#                     inheritable_tags=self.inheritable_tags,
#                     metadata=self.metadata,
#                     inheritable_metadata=self.inheritable_metadata,
#                 )
#             )
#
#         return managers
#
#     @classmethod
#     def configure(
#             cls,
#             inheritable_callbacks: Callbacks = None,
#             local_callbacks: Callbacks = None,
#             verbose: bool = False,
#             inheritable_tags: Optional[List[str]] = None,
#             local_tags: Optional[List[str]] = None,
#             inheritable_metadata: Optional[Dict[str, Any]] = None,
#             local_metadata: Optional[Dict[str, Any]] = None,
#     ) -> CallbackManager:
#         """Configure the callback manager.
#
#         Args:
#             inheritable_callbacks (Optional[Callbacks], optional): The inheritable
#                 callbacks. Defaults to None.
#             local_callbacks (Optional[Callbacks], optional): The local callbacks.
#                 Defaults to None.
#             verbose (bool, optional): Whether to enable verbose mode. Defaults to False.
#             inheritable_tags (Optional[List[str]], optional): The inheritable tags.
#                 Defaults to None.
#             local_tags (Optional[List[str]], optional): The local tags.
#                 Defaults to None.
#             inheritable_metadata (Optional[Dict[str, Any]], optional): The inheritable
#                 metadata. Defaults to None.
#             local_metadata (Optional[Dict[str, Any]], optional): The local metadata.
#                 Defaults to None.
#
#         Returns:
#             CallbackManager: The configured callback manager.
#         """
#         return _configure(
#             cls,
#             inheritable_callbacks,
#             local_callbacks,
#             verbose,
#             inheritable_tags,
#             local_tags,
#             inheritable_metadata,
#             local_metadata,
#         )
#
#
# T = TypeVar("T", CallbackManager, AsyncCallbackManager)
#
# H = TypeVar("H", bound=BaseCallbackHandler, covariant=True)
#
#
# def _configure(
#         callback_manager_cls: Type[T],
#         inheritable_callbacks: Callbacks = None,
#         local_callbacks: Callbacks = None,
#         verbose: bool = False,
#         inheritable_tags: Optional[List[str]] = None,
#         local_tags: Optional[List[str]] = None,
#         inheritable_metadata: Optional[Dict[str, Any]] = None,
#         local_metadata: Optional[Dict[str, Any]] = None,
# ) -> T:
#     """Configure the callback manager.
#
#         Args:
#             callback_manager_cls (Type[T]): The callback manager class.
#             inheritable_callbacks (Optional[Callbacks], optional): The inheritable
#                 callbacks. Defaults to None.
#             local_callbacks (Optional[Callbacks], optional): The local callbacks.
#                 Defaults to None.
#             verbose (bool, optional): Whether to enable verbose mode. Defaults to False.
#             inheritable_tags (Optional[List[str]], optional): The inheritable tags.
#                 Defaults to None.
#             local_tags (Optional[List[str]], optional): The local tags. Defaults to None.
#             inheritable_metadata (Optional[Dict[str, Any]], optional): The inheritable
#                 metadata. Defaults to None.
#             local_metadata (Optional[Dict[str, Any]], optional): The local metadata.
#                 Defaults to None.
#
#         Returns:
#             T: The configured callback manager.
#         """
#     from langchain_core.tracers.context import (
#         _configure_hooks,
#         _get_tracer_project,
#         _tracing_v2_is_enabled,
#         tracing_callback_var,
#         tracing_v2_callback_var,
#     )
#
#     run_tree = get_run_tree_context()
#     parent_run_id = None if run_tree is None else getattr(run_tree, "id")
#     callback_manager = callback_manager_cls(handlers=[], parent_run_id=parent_run_id)
#     if inheritable_callbacks or local_callbacks:
#         if isinstance(inheritable_callbacks, list) or inheritable_callbacks is None:
#             inheritable_callbacks_ = inheritable_callbacks or []
#             callback_manager = callback_manager_cls(
#                 handlers=inheritable_callbacks_.copy(),
#                 inheritable_handlers=inheritable_callbacks_.copy(),
#                 parent_run_id=parent_run_id,
#             )
#         else:
#             callback_manager = callback_manager_cls(
#                 handlers=inheritable_callbacks.handlers.copy(),
#                 inheritable_handlers=inheritable_callbacks.inheritable_handlers.copy(),
#                 parent_run_id=inheritable_callbacks.parent_run_id,
#                 tags=inheritable_callbacks.tags.copy(),
#                 inheritable_tags=inheritable_callbacks.inheritable_tags.copy(),
#                 metadata=inheritable_callbacks.metadata.copy(),
#                 inheritable_metadata=inheritable_callbacks.inheritable_metadata.copy(),
#             )
#         local_handlers_ = (
#             local_callbacks
#             if isinstance(local_callbacks, list)
#             else (local_callbacks.handlers if local_callbacks else [])
#         )
#         for handler in local_handlers_:
#             callback_manager.add_handler(handler, False)
#     if inheritable_tags or local_tags:
#         callback_manager.add_tags(inheritable_tags or [])
#         callback_manager.add_tags(local_tags or [], False)
#     if inheritable_metadata or local_metadata:
#         callback_manager.add_metadata(inheritable_metadata or {})
#         callback_manager.add_metadata(local_metadata or {}, False)
#
#     tracer = tracing_callback_var.get()
#     tracing_enabled_ = (
#             env_var_is_set("LANGCHAIN_TRACING")
#             or tracer is not None
#             or env_var_is_set("LANGCHAIN_HANDLER")
#     )
#
#     tracer_v2 = tracing_v2_callback_var.get()
#     tracing_v2_enabled_ = _tracing_v2_is_enabled()
#     tracer_project = _get_tracer_project()
#     debug = _get_debug()
#     if verbose or debug or tracing_enabled_ or tracing_v2_enabled_:
#         from langchain_core.tracers.langchain import LangChainTracer
#         from langchain_core.tracers.langchain_v1 import LangChainTracerV1
#         from langchain_core.tracers.stdout import ConsoleCallbackHandler
#
#         if verbose and not any(
#                 isinstance(handler, StdOutCallbackHandler)
#                 for handler in callback_manager.handlers
#         ):
#             if debug:
#                 pass
#             else:
#                 callback_manager.add_handler(StdOutCallbackHandler(), False)
#         if debug and not any(
#                 isinstance(handler, ConsoleCallbackHandler)
#                 for handler in callback_manager.handlers
#         ):
#             callback_manager.add_handler(ConsoleCallbackHandler(), True)
#         if tracing_enabled_ and not any(
#                 isinstance(handler, LangChainTracerV1)
#                 for handler in callback_manager.handlers
#         ):
#             if tracer:
#                 callback_manager.add_handler(tracer, True)
#             else:
#                 handler = LangChainTracerV1()
#                 handler.load_session(tracer_project)
#                 callback_manager.add_handler(handler, True)
#         if tracing_v2_enabled_ and not any(
#                 isinstance(handler, LangChainTracer)
#                 for handler in callback_manager.handlers
#         ):
#             if tracer_v2:
#                 callback_manager.add_handler(tracer_v2, True)
#             else:
#                 try:
#                     handler = LangChainTracer(project_name=tracer_project)
#                     callback_manager.add_handler(handler, True)
#                 except Exception as e:
#                     logger.warning(
#                         "Unable to load requested LangChainTracer."
#                         " To disable this warning,"
#                         " unset the LANGCHAIN_TRACING_V2 environment variables.",
#                         e,
#                     )
#     for var, inheritable, handler_class, env_var in _configure_hooks:
#         create_one = (
#                 env_var is not None
#                 and env_var_is_set(env_var)
#                 and handler_class is not None
#         )
#         if var.get() is not None or create_one:
#             var_handler = var.get() or cast(Type[BaseCallbackHandler], handler_class)()
#             if handler_class is None:
#                 if not any(
#                         handler is var_handler  # direct pointer comparison
#                         for handler in callback_manager.handlers
#                 ):
#                     callback_manager.add_handler(var_handler, inheritable)
#             else:
#                 if not any(
#                         isinstance(handler, handler_class)
#                         for handler in callback_manager.handlers
#                 ):
#                     callback_manager.add_handler(var_handler, inheritable)
#     return callback_manager
