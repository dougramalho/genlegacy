from src.tasks.tasks import process_task
from src.api.models import WelcomeTaskInput, DiscoveryTaskInput, ProcessCategory, QueryTaskInput
from src.utils import LLMStyleConsole

def main():
    print("inicializando")

    #console = LLMStyleConsole()
    
    while(True):
        
        #task_result = process_task(input_data.model_dump())
        welcome_input = WelcomeTaskInput()
        task_result = process_task(welcome_input)

        match task_result["output_data"]["result"]["category"]:
            case ProcessCategory.PROJECT_DISCOVERY:
                discovery_input = DiscoveryTaskInput(
                topic=ProcessCategory.PROJECT_DISCOVERY,
                )
                task_result = process_task(discovery_input)
            case ProcessCategory.OTHER:
                query = QueryTaskInput(query=task_result["output_data"]["result"]["message"])
                task_result = process_task(query)
            case ProcessCategory.GENERAL:
                query = QueryTaskInput(query=task_result["output_data"]["result"]["message"])
                task_result = process_task(query)
    
    #return task_result
    return True
    

if __name__ == "__main__":
    main()