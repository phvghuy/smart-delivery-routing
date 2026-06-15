from dataclasses import dataclass


@dataclass(frozen=True)
class Location:
    lat: float
    lng: float


@dataclass(frozen=True)
class Address:
    text: str
    location: Location


@dataclass(frozen=True)
class Load:
    weight: float
    volume: float


@dataclass(frozen=True)
class Money:
    amount: int
    currency: str = "VND"


@dataclass(frozen=True)
class Capacity:
    max_weight: float
    max_volume: float
