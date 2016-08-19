from actions.action_base import ActionBase


class ThankAction(ActionBase):
    def __init__(self):
        super().__init__(name="THANK",
                         keywords=['ty+', 'thanks+', 'thank you+', 'thankyou+', 'thx'],
                         answers=['np', 'np :)', 'no problem :D', 'no problem'])
