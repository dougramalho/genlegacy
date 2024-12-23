import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
src_dir = os.path.join(parent_dir, "src")
sys.path.append(parent_dir)
sys.path.append(src_dir)

from src.tasks.tasks import process_task
from src.api.models import InputDataModel

def test_process_task_welcome():
    input_data = {
        "commandName": "welcome",
        "message": "Preciso fazer o discovery de um projeto legado"
    }

    input_data = InputDataModel(**input_data)
    task_result = process_task(input_data.model_dump())
    return task_result


task_result = test_process_task_welcome()

if __name__ =="__main__":
    pytest.main()
