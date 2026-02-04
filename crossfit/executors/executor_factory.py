from crossfit.models.executor_models import ExecutorType
from crossfit.executors.local_executor import LocalExecutor

def create_executor(executor_type: ExecutorType, logger = None, catch: bool = True, **kwargs):
    """
    Factory method to create an executor based on the specified type.
    :param executor_type: The type of executor to create.
    :param logger: Optional logger instance for logging execution details.
    :param catch: Whether to catch exceptions during execution.
    :param kwargs: Additional keyword arguments for executor initialization.
    :return: An instance of the specified executor type.
    """
    if executor_type == ExecutorType.Local:
        return LocalExecutor(logger, catch, **kwargs)
    else:
        raise ValueError(f"Unknown executor type: {executor_type}")
