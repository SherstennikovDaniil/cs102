# Восьмое задание

## IPython notebook in Google Colab
Это задание нужно писать в тетрадке IPython. Версия для общих наработок будет тут.

Кнопка для открытия в Google Colab: [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/K3143-ITMO/Dementiy-assignments/blob/master/homework08-ds/Linear_Regression.ipynb)

## Примечания

* Для доступа к тетрадке нужно будет дать Colab доступ к своему аккаунту на Github. При открытии тетрадки Colab будет пару секунд дёргать окнами, выбивая из гитхаба доступ к файлу, это нормально.

* Если при открытии тетрадки возникает ошибка доступа, то нужно (после нажатия OK) поставить галочку `Include private repositories` и перезагрузить страницу.

* Сохранять просто так тетрадку нельзя. Можете или сделать себе копию на Google Drive или пользоваться `File -> Save to Github`.

## Проверка
`gradient_descent_tester` ([![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/K3143-ITMO/Dementiy-assignments/blob/master/homework08-ds/gradient_descent_tester.ipynb)) содержит небольшую проверку классов-регрессоров, просто закиньте ячейку с классом в секцию `Classes definitions`, убедитесь, что в секции `Testing` в функции `run_something_test()` передаётся правильное имя класса, и забирайте готовый `DataFrame` (ну или `.csv`-файл, смотря как удобнее).
Как всегда, никаких гарантий, если ничего не работает - чините сами/забейте и сравните руками.