from collections import namedtuple
from pullenti_client import Client
from pullenti.ner.geo.GeoReferent import GeoReferent

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
    def _special_processing_addr(object):
        addr_type = next(
            (x for x in object.slots if x.key == "TYP" or x.key == "TYPE"), None
        )
        name = next((x for x in object.slots if x.key == "NAME"), None)
        number = next((x for x in object.slots if x.key == "NUMBER"), None)

        result = [_.value for _ in [addr_type, name, number] if _ is not None]

        return " ".join(result)

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

            street = next((x for x in i.children if x.referent.label == "STREET"), None)
            if street:
                data["street"] = self._special_processing_addr(street.referent)

            city = self._get_city(i.children)
            if city:
                data["city"] = self._special_processing_addr(city.referent)

            region = self._get_region(i.children)
            if region:
                data["region"] = self._special_processing_addr(region.referent)

            items.append(Item(**data))
        return [PullentiAddrOutDto(**i._asdict()) for i in items]

    def _get_city(self, children):
        if len(children) == 0:
            return None

        geo = next(
            (
                x
                for x in children
                if x.referent.label == "GEO"
                and GeoReferent._GeoReferent__is_city(str(x.referent.slots))
            ),
            None,
        )

        if geo:
            return geo
        else:
            return self._get_city(children=children.children)

    def _get_region(self, children):
        if len(children) == 0:
            return None

        geo = next(
            (
                x
                for x in children
                if x.referent.label == "GEO"
                and GeoReferent._GeoReferent__is_region(str(x.referent.slots))
            ),
            None,
        )

        if geo:
            return geo
        else:
            return self._get_region(children=children.children)
