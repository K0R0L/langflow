from langflow.custom import Component
from langflow.io import MessageInput, Output
from langflow.schema import Data
from langflow.schema.message import Message
from loguru import logger


class ParsePathKeyComponent(Component):
    display_name = "ParsePathKey"
    description = "Split message to path and key."
    icon = "message-square-share"
    beta = True
    name = "MessagetoData"

    inputs = [
        MessageInput(
            name="message",
            display_name="Message",
            info="The Message object to convert to a Data object",
        ),
    ]

    outputs = [
        Output(display_name="Directory", name="directory", method="get_directory"),
        Output(display_name="Key", name="key", method="get_key"),
    ]

    def get_directory(self) -> Message:
        if isinstance(self.message, Message):
            directory = str(self.message.text).split(",")[0].split(":")[1]
            return Message(text=directory)
            

        msg = "Error converting Message to Data: Input must be a Message object"
        logger.opt(exception=True).debug(msg)
        self.status = msg
        return Data(data={"error": msg})
        
    def get_key(self) -> Message:
        if isinstance(self.message, Message):
            directory = str(self.message.text).split(",")[1].split(":")[1]
            #raise Exception(f"{directory=}")
            return Message(text=directory)
            

        msg = "Error converting Message to Data: Input must be a Message object"
        logger.opt(exception=True).debug(msg)
        self.status = msg
        return Data(data={"error": msg})
        

