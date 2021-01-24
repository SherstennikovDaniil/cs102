import datetime as dt
import statistics
import typing as tp

from dateutil.relativedelta import relativedelta

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.
    Возраст считается как медиана среди возраста всех друзей пользователя
    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    ages: tp.List[float] = []
    friends = get_friends(user_id, fields=["bdate"])
    for friend in friends.items:
        if (
            "bdate" in friend and str(friend["bdate"]).count(".") == 2  # type: ignore
        ):
            birth_date = dt.datetime.strptime(friend["bdate"], "%d.%m.%Y")  # type: ignore
            age = relativedelta(dt.datetime.now(), birth_date).years
            ages.append(age)
    if not ages:
        return None
    return statistics.median(ages)