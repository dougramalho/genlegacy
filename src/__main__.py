from src.tasks.tasks import process_task
from src.api.models import WelcomeTaskInput, DiscoveryTaskInput, ProcessCategory

def main():
    print("inicializando")

    welcome_input = WelcomeTaskInput()
    task_result = process_task(welcome_input)

    #task_result = process_task(input_data.model_dump())

    match task_result["output_data"]["result"]["category"]:
        case ProcessCategory.PROJECT_DISCOVERY:
            discovery_input = DiscoveryTaskInput(
            topic=ProcessCategory.PROJECT_DISCOVERY,
            )
            task_result = process_task(discovery_input)
    
    
    print(task_result)

    return task_result
    

if __name__ == "__main__":
    main()