from pyedgar.utils.mixins.base_mixin import BaseMixin
from pyedgar.utils.ticker_cte_map import TickerCTEMap


class TickerCTEMapMixin(BaseMixin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ticker_cte_map = TickerCTEMap(self._network_client, **kwargs)


