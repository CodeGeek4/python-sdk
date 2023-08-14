from .zero_knowledge_proof import ZeroKnowledgeProof
from ._model_transpiler import _get_model_transpiler
import os

class LeoTranspiler:
    def __init__(self, model, validation_data=None, model_as_input=False, ouput_model_hash=None):
        """
        Create a new transpiler instance.

        Parameters
        ----------
        model : Model
            The model to transpile.
        validation_data : tuple of array_like, optional
            Data on which to evaluate the numerical stability of the circuit. The model will not be trained on
            this data.
        model_as_input : bool, optional
            If True, the model weights and biases are treated as circuit input instead of being hardcoded.
        ouput_model_hash : str, optional
            If set, the circuit will return the hash of the model weights and biases. Possible values are ... (todo)

        Returns
        -------
        LeoTranspiler
            The transpiler instance.
        """

        self.model = model
        self.validation_data = validation_data
        self.model_as_input = model_as_input
        self.ouput_model_hash = ouput_model_hash

        self.transpilation_result = None
        self.leo_program_stored = False

    def store_leo_program(self, path, project_name):
        """
        Store the Leo program to a file.

        Parameters
        ----------
        path : str
            The path to the file to store the Leo program in.

        Returns
        -------
        None
        """ 

        model_transpiler = _get_model_transpiler(self.model, self.validation_data)

        # Check numeric stability for model and data and get number range
        model_transpiler._numbers_get_leo_type_and_fixed_point_scaling_factor()

        if self.transpilation_result is None:
            print("Transpiling model...")
            self.transpilation_result = model_transpiler.transpile(project_name) # todo check case when project name changes

        project_dir = os.path.join(path, project_name)
        src_folder_dir = os.path.join(project_dir, "src")
        leo_file_dir = os.path.join(src_folder_dir, "main.leo")

        # Make sure path exists
        os.makedirs(src_folder_dir, exist_ok=True)

        with open(leo_file_dir, "w") as f:
            f.write(self.transpilation_result)

        program_json = self._get_program_json(project_name)
        program_json_file_dir = os.path.join(project_dir, "program.json")
        with open(program_json_file_dir, "w") as f:
            f.write(program_json)

        self.leo_program_stored = True
        print("Leo program stored")

    def prove(self, input):
        """
        Prove the model output for a given input.

        Parameters
        ----------
        input : array_like
            The input for which to prove the output.

        Returns
        -------
        ZeroKnowledgeProof
            The zero-knowledge proof for the given input.
        """
        if not self.leo_program_stored:
            raise Exception("Leo program not stored")
        
        circuit_input = None # TODO: organize circuit input
        circuit_output, proof_value = None, None # TODO: here we need to do the FFI call or CLI call for leo/snarkVM execute
        return ZeroKnowledgeProof(circuit_input, circuit_output, proof_value)
    
    def _get_program_json(self, project_name):
        """
        Generate the program.json file content.

        Parameters
        ----------
        project_name : str
            The name of the project.

        Returns
        -------
        str
            The program.json file.
        """
        return f"""{{
    "program": "{project_name}.aleo",
    "version": "0.0.0",
    "description": "transpiler generated program",
    "license": "MIT"
}}"""