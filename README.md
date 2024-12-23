# DAG Pipeline System

This project implements a DAG (Directed Acyclic Graph) based pipeline system, similar to the concept used in Apache Airflow. The system enables the execution of different tasks in sequence, where each task can initiate different pipelines based on its processing category.

## Project Structure

```
src/
├── api/
│   └── models.py          # Data model definitions
├── pipelines/
│   ├── registry.py        # Central pipeline registry
│   ├── project/
│   │   └── project_discovery_pipeline.py
│   └── orchestration/
│       └── manager_classifier_pipeline.py
└── tasks/
    └── tasks.py          # Task processing logic
```

## Core Components

### Data Models (`models.py`)

The system uses Pydantic classes to ensure data validation and type safety. The main models include:

- `BaseTaskInput`: Base class for all tasks
- `WelcomeTaskInput`: Initial system task
- `DiscoveryTaskInput`: Project discovery task
- `ProcessingContext`: Pipeline processing context
- `OutputDataModel`: Output data model
- `TaskResult`: Final task processing result

### Pipeline Registry (`registry.py`)

The `PipelineRegistry` maintains a mapping between task types and their respective pipelines:

```python
_pipeline_mapping = {
    WelcomeTaskInput: InitializeSessionPipeline,
    DiscoveryTaskInput: ProjectDiscoveryPipeline
}
```

### Task Processing (`tasks.py`)

The `tasks.py` module contains the core logic for task processing, including:
- Identifying the appropriate pipeline
- Executing the pipeline
- Generating the task result

## Execution Flow

1. An initial task is created (usually `WelcomeTaskInput`)
2. The system processes the task through `process_task()`
3. Based on the returned category, a new task may be created and processed
4. The final result is returned with all processing information

## How to Use

### Running the System

```python
from src.api.models import WelcomeTaskInput
from src.tasks.tasks import process_task

# Create and process initial task
welcome_input = WelcomeTaskInput()
task_result = process_task(welcome_input)

# Result includes status, input/output data, and processing context
print(task_result)
```

### Adding a New Task

1. Create new input class:
```python
class AnalysisTaskInput(BaseTaskInput):
    command_name: str = "analysis"
    project_id: str
    analysis_type: str
```

2. Create new pipeline:
```python
class ProjectAnalysisPipeline(BasePipeline):
    def run(self, input_data: AnalysisTaskInput) -> Tuple[Dict, Dict]:
        # Specific implementation
        pass
```

3. Register in PipelineRegistry:
```python
PipelineRegistry._pipeline_mapping[AnalysisTaskInput] = ProjectAnalysisPipeline
```

## Design Benefits

- **Type-Safe**: Extensive use of type hints and Pydantic validation
- **Extensible**: Easy addition of new tasks and pipelines
- **Maintainable**: Clear separation of concerns
- **Flexible**: Support for different types of tasks and processing
- **Testable**: Easy to unit test individual components

## Technical Requirements

- Python 3.7+
- Pydantic 2.0+
- Additional dependencies as specified in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dag-pipeline-system.git
cd dag-pipeline-system
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project follows PEP 8 guidelines. Before committing, please run:
```bash
black .
flake8
```

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

Common issues and their solutions:

### Pipeline Not Found
If you encounter a "Pipeline Not Found" error, ensure that:
- Your task type is properly registered in the PipelineRegistry
- The import paths are correct
- The task class name matches the registry mapping

### Circular Import Errors
If you encounter circular import errors:
- Ensure all base classes are defined in `models.py`
- Use lazy imports where necessary
- Consider restructuring the affected modules

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Apache Airflow's DAG concept
- Built with modern Python practices and type safety in mind