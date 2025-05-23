import json
import re

from langflow.custom import Component
from langflow.io import MessageInput, Output
from langflow.schema import Data
from langflow.schema.message import Message
from loguru import logger


class ParsePathKeyComponent(Component):
    display_name = "ParsePathKey"
    description = "Split message to path, filters and output fields."
    icon = "message-square-share"
    name = "ParsePathKey"

    inputs = [
        MessageInput(
            name="message",
            display_name="Message",
            info="The Message object containing structured text with path, filters and output fields",
        ),
    ]

    outputs = [
        Output(display_name="Directory", name="directory", method="get_directory"),
        Output(display_name="Key", name="key", method="get_key"),
        Output(display_name="Output_key", name="output_key", method="get_output_key"),
    ]

    def _parse_message(self):
        """Parse message into components: path, filters, and output fields"""
        if not hasattr(self, 'message') or self.message is None:
            logger.error("No message provided")
            return None, None, None

        if isinstance(self.message, Message):
            message_text = str(self.message.text).strip()
            try:
                path_match = re.search(r'path:\s*([^;]+)', message_text)
                path = path_match.group(1).strip() if path_match else ""
                
                filters_match = re.search(r'filters:\s*(\[.+?\])', message_text, re.DOTALL)
                filters_str = filters_match.group(1) if filters_match else "[]"
                
                filters_str = filters_str.replace("'", '"')
                filters_str = re.sub(r'(\w+):', r'"\1":', filters_str)
                filters = json.loads(filters_str)
                
                output_match = re.search(r'output:\s*(\[.+?\])', message_text, re.DOTALL)
                output_str = output_match.group(1) if output_match else "[]"
                output_str = output_str.replace("'", '"')
                output_str = re.sub(r'(\w+)', r'"\1"', output_str.replace('"', ''))
                output_fields = json.loads(output_str)
                
                return path, filters, output_fields
            
            except Exception as e:
                logger.error(f"Error parsing message: {str(e)}")
                logger.error(f"Message text: {message_text}")
                return "", [], []
                
        return "", [], []

    def get_directory(self) -> Message:
        """Return the directory path"""
        path, _, _ = self._parse_message()
        return Message(text=path)
        
    def get_key(self) -> Data:
        """Return filters configuration"""
        _, filters, _ = self._parse_message()
        return Data(data={"filters":filters})
        
    def get_output_key(self) -> Data:
        """Return output fields"""
        _, _, output_fields = self._parse_message()
        return Data(data={"output_keys":output_fields})