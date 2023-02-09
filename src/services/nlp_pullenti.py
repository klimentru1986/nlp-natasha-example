from collections import namedtuple
from functools import reduce
from pullenti_client import Client
from pullenti.ner.geo.GeoReferent import GeoReferent

from src.dto.predict_in_dto import PredictInDto
from src.dto.pullenti_addr_out_dto import PullentiAddrOutDto
from src.dto.pullenti_names_out_dto import PullentiNamesOutDto


class NlpPullenti:
    def predict(self, predict_dto: PredictInDto):
        client = Client("pullenti-server", 8080)

        doc = client(predict_dto.text)

        return {
            "names": self._get_names(doc),
            "addr": self._get_addr(doc),
        }

    def _get_names(self, src):
        sources = [m for m in src.matches if m.referent.label == "PERSON"]

        items = []
        valid_fields = PullentiNamesOutDto.__annotations__.keys()
        Item = namedtuple("Item", valid_fields, defaults=[None] * len(valid_fields))

        for i in sources:
            data = {
                str(s.key.lower()): s.value
                for s in i.referent.slots
                if s.key.lower() in valid_fields and isinstance(s.value, str)
            }

            items.append(Item(**data))

        items = list(dict.fromkeys(items))
        return [PullentiNamesOutDto(**i._asdict()) for i in items]

    @staticmethod
    def _special_processing_addr(object):
        addr_type = next((x for x in object.slots if x.key in ["TYP", "TYPE"]), None)
        name = next((x for x in object.slots if x.key == "NAME"), None)
        number = next((x for x in object.slots if x.key == "NUMBER"), None)

        result = [_.value for _ in [addr_type, name, number] if _ is not None]

        return " ".join(result)

    def _get_addr(self, src):
        sources = [m for m in src.matches if m.referent.label == "ADDRESS"]
        person_matchers = [m for m in src.matches if m.referent.label == "PERSON"]
        person_sources = self._flat_map_children(person_matchers)
        person_sources = [
            m for m in person_sources if m.referent.label == "ADDRESS"
        ]

        sources = [*sources, *person_sources]

        items = []
        valid_fields = PullentiAddrOutDto.__annotations__.keys()
        Item = namedtuple("Item", valid_fields, defaults=[None] * len(valid_fields))

        for i in sources:
            data = {
                str(s.key.lower()): s.value
                for s in i.referent.slots
                if s.key.lower() in valid_fields and isinstance(s.value, str)
            }

            if street := next(
                (x for x in i.children if x.referent.label == "STREET"), None
            ):
                data["street"] = self._special_processing_addr(street.referent)

            if city := self._get_city(i.children):
                data["city"] = self._special_processing_addr(city.referent)

            if region := self._get_region(i.children):
                data["region"] = self._special_processing_addr(region.referent)

            items.append(Item(**data))

        items = list(dict.fromkeys(items))
        return [PullentiAddrOutDto(**i._asdict()) for i in items]

    def _get_city(self, children):
        if len(children) == 0:
            return None

        if geo := next(
            (
                x
                for x in children
                if x.referent.label == "GEO"
                and GeoReferent._GeoReferent__is_city(str(x.referent.slots))
            ),
            None,
        ):
            return geo
        ch = self._flat_map_children(children)
        return self._get_city(children=ch)

    def _get_region(self, children):
        if len(children) == 0:
            return None

        if geo := next(
            (
                x
                for x in children
                if x.referent.label == "GEO"
                and GeoReferent._GeoReferent__is_region(str(x.referent.slots))
            ),
            None,
        ):
            return geo
        ch = self._flat_map_children(children)
        return self._get_region(children=ch)

    @staticmethod
    def _flat_map_children(arr):
        list_of_children = [_.children for _ in arr]
        return reduce(list.__add__, list_of_children)
