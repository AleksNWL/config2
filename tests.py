import unittest
from unittest.mock import patch, MagicMock
import json
from pathlib import Path
from visualizer import DependencyVisualizer


class TestDependencyVisualizer(unittest.TestCase):
    def setUp(self):
        self.config = {
            "graphviz_path": "/usr/local/bin/plantuml",
            "package_name": "requests",
            "output_file": "test_dependencies.puml",
            "max_depth": 2,
            "repository_url": "https://pypi.org/project/requests/"
        }
        self.config_path = "test_config.json"
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f)

        self.visualizer = DependencyVisualizer(self.config_path)

    def tearDown(self):
        if Path(self.config_path).exists():
            Path(self.config_path).unlink()
        if Path(self.config['output_file']).exists():
            Path(self.config['output_file']).unlink()

    def test_load_config(self):
        config = self.visualizer.load_config(self.config_path)
        self.assertEqual(config, self.config)

    @patch('importlib.metadata.distribution')
    def test_get_dependencies(self, mock_distribution):
        
        mock_dist = MagicMock()
        mock_dist.requires = ["urllib3 (>=1.21.1,<2.0)"]
        mock_distribution.return_value = mock_dist

        dependencies = self.visualizer.get_dependencies("requests", depth=0)
        self.assertIn("urllib3", dependencies)

    def test_generate_plantuml(self):
        dependencies = {
            "requests": {
                "urllib3": {}
            }
        }
        plantuml_code = self.visualizer.generate_plantuml(dependencies)
        print("Generated PlantUML code:")
        print(plantuml_code)

    
        self.assertIn('"requests" -> "urllib3";', plantuml_code)
        self.assertTrue(plantuml_code.startswith("@startuml"))
        self.assertTrue(plantuml_code.endswith("@enduml"))

    def test_save_output(self):
        test_content = "Test PlantUML Content"
        self.visualizer.save_output(test_content)
        saved_content = Path(self.config['output_file']).read_text()
        self.assertEqual(saved_content, test_content)


if __name__ == "__main__":
    unittest.main()


# python visualizer.py C:/Users/Grifo/configProg/conf2/config.json