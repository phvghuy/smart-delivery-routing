from .repositories import HubQueryRepository
from .dto import HubQuery, PagedHubs


class ListHubsUseCase:
    def __init__(self, repo: HubQueryRepository):
        self._repo = repo

    def execute(self, query: HubQuery) -> PagedHubs:
        items, total = self._repo.list(query)
        return PagedHubs(
            items=items, 
            total=total, 
            page=query.page, 
            size=query.page_size,
        )
