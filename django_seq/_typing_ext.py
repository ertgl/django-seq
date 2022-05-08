from typing import (
    Any,
    Generic,
    Type,
    TypeVar,
)


__all__ = (
    'mimic_generic_type',
)


T_contra = TypeVar('T_contra', contravariant=True)


class _GenericLikeType(
    Generic[T_contra]
):

    type_: Type[T_contra]

    def __init__(
        self,
        type_: Type[T_contra],
    ) -> None:
        self.type_ = type_

    def __getitem__(
        self,
        *args: Any,
    ) -> Type[T_contra]:
        return self.type_


def mimic_generic_type(
    type_: Type[T_contra],
) -> Type[T_contra]:
    return _GenericLikeType(type_)  # type: ignore[return-value]
