from collections import namedtuple
from pullenti_client import Client

from src.dto.predict_in_dto import PredictInDto
from src.dto.pullenti_addr_out_dto import PullentiAddrOutDto
from src.dto.pullenti_names_out_dto import PullentiNamesOutDto


class NlpPullenti:
    def predict(self, predict_dto: PredictInDto):
        client = Client("pullenti-server", 8080)

        doc = client(predict_dto.text)

        result = {
            "names": self._get_names(doc),
            "addr": self._get_addr(doc),
        }

        return result

    def _get_names(self, src):
        sources = [m for m in src.matches if m.referent.label == "PERSON"]

        items = list()
        valid_fields = PullentiNamesOutDto.__annotations__.keys()
        Item = namedtuple("Item", valid_fields, defaults=[None] * len(valid_fields))

        for i in sources:
            data = {
                str(s.key.lower()): s.value
                for s in i.referent.slots
                if s.key.lower() in valid_fields and isinstance(s.value, str)
            }

            items.append(Item(**data))
        return [PullentiNamesOutDto(**i._asdict()) for i in items]

    @staticmethod
    def _special_processing_street(object):

        name = next((x for x in object.slots if x.key == "NAME"), None)
        return name.value

    def _get_addr(self, src):
        sources = [m for m in src.matches if m.referent.label == "ADDRESS"]

        items = list()
        valid_fields = PullentiAddrOutDto.__annotations__.keys()
        Item = namedtuple("Item", valid_fields, defaults=[None] * len(valid_fields))

        for i in sources:
            data = {
                str(s.key.lower()): s.value
                for s in i.referent.slots
                if s.key.lower() in valid_fields and isinstance(s.value, str)
            }

            children = list(i.children)
            for c in children:
                if c.children:
                    children.append(*c.children)

            street = next((x for x in children if x.referent.label == "STREET"), None)
            if street:
                data["street"] = self._special_processing_street(street.referent)

            geo = next((x for x in children if x.referent.label == "GEO"), None)
            if geo:
                data["geo"] = self._special_processing_street(geo.referent)

            items.append(Item(**data))
        return [PullentiAddrOutDto(**i._asdict()) for i in items]
