import aiosqlite
import aiofiles
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from decouple import config

bot = Bot(token=config("BOT_TOKEN"))
dp = Dispatcher()

quiz_questions = [
    {
        "question": "1. Что такое атом?",
        "options": ["Часть молекулы", "Наименьшая часть химического элемента", "Заряженная частица"],
        "correct": "Наименьшая часть химического элемента"
    },
    {
        "question": "2. Кто предложил планетарную модель атома?",
        "options": ["Дж. Дж. Томсон", "Эрнест Резерфорд", "Нильс Бор"],
        "correct": "Эрнест Резерфорд"
    },
    {
        "question": "3. Что такое атомный номер?",
        "options": ["Число нейтронов в ядре", "Сумма протонов и нейтронов", "Число протонов в ядре"],
        "correct": "Число протонов в ядре"
    },
    {
        "question": "4. Что такое массовое число?",
        "options": ["Число протонов", "Сумма протонов и нейтронов", "Число электронов"],
        "correct": "Сумма протонов и нейтронов"
    },
    {
        "question": "5. Что такое изотопы?",
        "options": ["Атомы с одинаковым числом протонов и разным числом нейтронов", "Атомы с разным зарядом ядра", "Атомы разных элементов"],
        "correct": "Атомы с одинаковым числом протонов и разным числом нейтронов"
    },
    {
        "question": "6. Заряд ядра атома определяется...",
        "options": ["Числом нейтронов", "Числом электронов", "Числом протонов"],
        "correct": "Числом протонов"
    },
    {
        "question": "7. В нейтральном атоме число протонов...",
        "options": ["Больше числа электронов", "Равно числу электронов", "Меньше числа электронов"],
        "correct": "Равно числу электронов"
    },
    {
        "question": "8. Отрицательно заряженная частица атома - это...",
        "options": ["Протон", "Нейтрон", "Электрон"],
        "correct": "Электрон"
    },
    {
        "question": "9. Частица, не имеющая электрического заряда, - это...",
        "options": ["Протон", "Нейтрон", "Электрон"],
        "correct": "Нейтрон"
    },
    {
        "question": "10. Где сосредоточена основная масса атома?",
        "options": ["В электронной оболочке", "В ядре", "Равномерно распределена"],
        "correct": "В ядре"
    },
    {
        "question": "11. Модель атома «Пудинг с изюмом» предложил...",
        "options": ["Эрнест Резерфорд", "Дж. Дж. Томсон", "Демокрит"],
        "correct": "Дж. Дж. Томсон"
    },
    {
        "question": "12. Опыт по рассеянию α-частиц привел к созданию модели атома...",
        "options": ["Квантовой", "Планетарной", "«Пудинг с изюмом»"],
        "correct": "Планетарной"
    },
    {
        "question": "13. Что такое электронная орбиталь?",
        "options": ["Траектория движения электрона", "Область пространства вокруг ядра, где вероятно нахождение электрона", "Определенная орбита электрона"],
        "correct": "Область пространства вокруг ядра, где вероятно нахождение электрона"
    },
    {
        "question": "14. Максимальное число электронов на энергетическом уровне рассчитывается по формуле:",
        "options": ["2n", "n²", "2n²"],
        "correct": "2n²"
    },
    {
        "question": "15. Сколько электронов может максимально находиться на s-орбитали?",
        "options": ["2", "6", "10"],
        "correct": "2"
    },
    {
        "question": "16. Сколько электронов может максимально находиться на p-орбитали?",
        "options": ["2", "6", "10"],
        "correct": "6"
    },
    {
        "question": "17. Сколько электронов может максимально находиться на d-орбитали?",
        "options": ["6", "10", "14"],
        "correct": "10"
    },
    {
        "question": "18. Какой формы s-орбиталь?",
        "options": ["Гантелеобразная", "Сферическая", "Сложной формы"],
        "correct": "Сферическая"
    },
    {
        "question": "19. Что такое электронная конфигурация?",
        "options": ["Распределение электронов по орбиталям", "Число протонов в ядре", "Размер атома"],
        "correct": "Распределение электронов по орбиталям"
    },
    {
        "question": "20. Принцип, согласно которому электроны занимают свободные орбитали с наименьшей энергией, называется...",
        "options": ["Принцип Паули", "Правило Хунда", "Принцип наименьшей энергии"],
        "correct": "Принцип наименьшей энергии"
    },
    {
        "question": "21. Правило, гласящее, что «в пределах подуровня электроны располагаются так, чтобы их суммарный спин был максимальным» - это...",
        "options": ["Принцип Паули", "Правило Хунда", "Правило Клечковского"],
        "correct": "Правило Хунда"
    },
    {
        "question": "22. Ne, Ar, Xe, Kr ",
        "options": ["В животах светлячков", "Инертны", "Интровертны"],
        "correct": "Инертны"
    },
    {
        "question": "23. Что показывает главное квантовое число?",
        "options": ["Форму ленты Мёбиуса", "Энергетический уровень", "Ориентацию орбитали вне пространства"],
        "correct": "Энергетический уровень"
    },
    {
        "question": "24. Спиновое квантовое число характеризует...",
        "options": ["Энергию электрона", "Собственное вращение электрона", "Форму орбитали"],
        "correct": "Собственное вращение электрона"
    },
    {
        "question": "25. Валентные электроны - это...",
        "options": ["Все электроны атома", "Электроны внутренних уровней", "Электроны внешнего энергетического уровня"],
        "correct": "Электроны внешнего энергетического уровня"
    },
    {
        "question": "26. Ион - это...",
        "options": ["Нейтральный атом", "Электрически заряженная частица", "Разновидность изотопа"],
        "correct": "Электрически заряженная частица"
    },
    {
        "question": "27. Катион - это ион с...",
        "options": ["Отрицательным зарядом", "Положительным зарядом", "Нулевым зарядом"],
        "correct": "Положительным зарядом"
    },
    {
        "question": "28. Анион - это ион с...",
        "options": ["Отрицательным зарядом", "Положительным зарядом", "Нулевым зарядом"],
        "correct": "Отрицательным зарядом"
    },
    {
        "question": "29. Атом, потерявший электрон, превращается в...",
        "options": ["Анион", "Катион", "Остается атомом"],
        "correct": "Катион"
    },
    {
        "question": "30. Атом, принявший электрон, превращается в...",
        "options": ["Анион", "Катион", "Остается атомом"],
        "correct": "Анион"
    },
    {
        "question": "31. Свойства элементов находятся в периодической зависимости от...",
        "options": ["Атомной массы", "Заряда ядра атома", "Числа нейтронов"],
        "correct": "Заряда ядра атома"
    },
    {
        "question": "32. Период в Периодической системе - это...",
        "options": ["Вертикальный ряд", "Горизонтальный ряд", "Блок элементов"],
        "correct": "Горизонтальный ряд"
    },
    {
        "question": "33. Группа в Периодической системе - это...",
        "options": ["Вертикальный ряд", "Горизонтальный ряд", "Блок элементов"],
        "correct": "Вертикальный ряд"
    },
    {
        "question": "34. Элементы главных подгрупп характеризуются тем, что у них...",
        "options": ["Заполняется s- и p-подуровень", "Заполняется d-подуровень", "Заполняется f-подуровень"],
        "correct": "Заполняется s- и p-подуровень"
    },
    {
        "question": "35. Элементы, в атомах которых происходит заполнение d-орбиталей, называются...",
        "options": ["s-элементы", "p-элементы", "d-элементы"],
        "correct": "d-элементы"
    },
    {
        "question": "36. Радиус атома...",
        "options": ["Увеличивается слева направо по периоду", "Увеличивается сверху вниз по группе", "Уменьшается сверху вниз по группе"],
        "correct": "Увеличивается сверху вниз по группе"
    },
    {
        "question": "37. Энергия ионизации - это энергия, необходимая для...",
        "options": ["Отрыва электрона от атома", "Присоединения электрона к атому", "Возбуждения атома"],
        "correct": "Отрыва электрона от атома"
    },
    {
        "question": "38. Сродство к электрону - это энергия, которая...",
        "options": ["Выделяется при присоединении электрона", "Поглощается при присоединении электрона", "Необходима для отрыва электрона"],
        "correct": "Выделяется при присоединении электрона"
    },
    {
        "question": "39. Электроотрицательность - это способность атома...",
        "options": ["Отдавать электроны", "Притягивать электроны в химической связи", "Проводить электрический ток"],
        "correct": "Притягивать электроны в химической связи"
    },
    {
        "question": "40. Самый электроотрицательный элемент - это...",
        "options": ["Кислород (O)", "Хлор (Cl)", "Фтор (F)"],
        "correct": "Фтор (F)"
    },
    {
        "question": "41. Атом какого элемента имеет наименьший радиус?",
        "options": ["Водород (H)", "Гелий (He)", "Франций (Fr)"],
        "correct": "Гелий (He)"
    },
    {
        "question": "42. Какой элемент имеет электронную конфигурацию 1s²2s²2p⁶3s²3p⁶4s¹?",
        "options": ["Калий (K)", "Кальций (Ca)", "Натрий (Na)"],
        "correct": "Калий (K)"
    },
    {
        "question": "43. Сколько протонов, нейтронов и электронов в атоме Кислорода?",
        "options": ["p⁺=8, n⁰=8, e⁻=8", "p⁺=16, n⁰=8, e⁻=8", "p⁺=8, n⁰=16, e⁻=8"],
        "correct": "p⁺=8, n⁰=8, e⁻=8"
    },
    {
        "question": "44. Чему равен заряд ядра атома углерода?",
        "options": ["+6", "+12", "+4"],
        "correct": "+6"
    },
    {
        "question": "45. Сколько энергетических уровней у атома натрия?",
        "options": ["2", "3", "4"],
        "correct": "3"
    },
    {
        "question": "46. Сколько электронов на внешнем уровне у атома азота?",
        "options": ["3", "5", "7"],
        "correct": "5"
    },
    {
        "question": "47. Атом какого элемента имеет электронную конфигурацию ...3s²3p⁵?",
        "options": ["Сера (S)", "Хлор (Cl)", "Фтор (F)"],
        "correct": "Хлор (Cl)"
    },
    {
        "question": "48. Какой элемент является инертным газом?",
        "options": ["Азот (N)", "Кислород (O)", "Аргон (Ar)"],
        "correct": "Аргон (Ar)"
    },
    {
        "question": "49. Что общего у изотопов одного элемента?",
        "options": ["Массовое число", "Число нейтронов", "Число протонов"],
        "correct": "Число протонов"
    },
    {
        "question": "50. Чем отличаются изотопы одного элемента?",
        "options": ["Зарядом ядра", "Числом нейтронов", "Числом электронов"],
        "correct": "Числом нейтронов"
    },
    {
        "question": "51. Явление существования изотопов называется...",
        "options": ["Изомерия", "Изотопия", "Аллотропия"],
        "correct": "Изотопия"
    },
    {
        "question": "52. Атомная масса элемента, указанная в периодической таблице, - это...",
        "options": ["Масса самого распространенного изотопа", "Средняя масса всех природных изотопов", "Масса числа протонов"],
        "correct": "Средняя масса всех природных изотопов"
    },
    {
        "question": "53. Квантовая механика описывает движение...",
        "options": ["Только макротел", "Только элементарных частиц", "Частиц в микромире"],
        "correct": "Частиц в микромире"
    },
    {
        "question": "54. Орбитали с одинаковым значением главного квантового числа образуют...",
        "options": ["Уровень", "Подуровень", "0рбиталь"],
        "correct": "Уровень"
    },
    {
        "question": "55. Орбитали, отличающиеся магнитным квантовым числом, имеют...",
        "options": ["Разную энергию", "Одинаковую энергию (вырожденны)", "Разную форму"],
        "correct": "Одинаковую энергию (вырожденны)"
    },
    {
        "question": "56. Максимальное число электронов на третьем энергетическом уровне?",
        "options": ["8", "18", "32"],
        "correct": "18"
    },
    {
        "question": "57. Какой подуровень заполняется после 4s?",
        "options": ["4p", "3d", "4d"],
        "correct": "3d"
    },
    {
        "question": "58. Атом какого элемента имеет полностью завершенный второй энергетический уровень?",
        "options": ["Азот (N)", "Неон (Ne)", "Кислород (O)"],
        "correct": "Неон (Ne)"
    },
    {
        "question": "59. Электронная формула кальция (Ca)...",
        "options": ["1s²2s²2p⁶3s²3p⁶4s²", "1s²2s²2p⁶3s²3p⁶3d²", "1s²2s²2p⁶3s²3p⁶4s¹3d¹"],
        "correct": "1s²2s²2p⁶3s²3p⁶4s²"
    },
    {
        "question": "60. Элемент с полностью завершенным внешним уровнем - это...",
        "options": ["Щелочной металл", "Галоген", "Инертный газ"],
        "correct": "Инертный газ"
    },
    {
        "question": "61. Атомы щелочных металлов имеют на внешнем уровне...",
        "options": ["1 электрон", "2 электрона", "7 электронов"],
        "correct": "1 электрон"
    },
    {
        "question": "62. Атомы галогенов имеют на внешнем уровне...",
        "options": ["1 электрон", "2 электрона", "7 электронов"],
        "correct": "7 электронов"
    },
    {
        "question": "63. В каком порядке заполняются электронами орбитали?",
        "options": ["По увеличению номера уровня", "По увеличению энергии", "В произвольном порядке"],
        "correct": "По увеличению энергии"
    },
    {
        "question": "64. Кто создал современную периодическую систему элементов?",
        "options": ["Д.И. Менделеев", "Э. Резерфорд", "Дж. Дальтон"],
        "correct": "Д.И. Менделеев"
    },
    {
        "question": "65. Спин электрона - это...",
        "options": ["Собственный момент импульса электрона", "Заряд электрона", "Масса электрона"],
        "correct": "Собственный момент импульса электрона"
    },
    {
        "question": "66. Магнитное квантовое число определяет...",
        "options": ["Энергию уровня", "Форму орбитали", "Ориентацию орбитали в пространстве"],
        "correct": "Ориентацию орбитали в пространстве"
    },
    {
        "question": "67. Орбитальное квантовое число определяет...",
        "options": ["Энергию уровня", "Форму орбитали (подуровень)", "Ориентацию орбитали"],
        "correct": "Форму орбитали (подуровень)"
    },
    {
        "question": "68. Какое значение орбитального квантового числа для f-орбитали?",
        "options": ["0", "1", "3"],
        "correct": "3"
    },
    {
        "question": "69. Сколько f-орбиталей на одном подуровне?",
        "options": ["1", "3", "7"],
        "correct": "7"
    },
    {
        "question": "70. Какой элемент имеет самую высокую энергию ионизации в своем периоде?",
        "options": ["Щелочной металл", "Инертный газ", "Галоген"],
        "correct": "Инертный газ"
    },
    {
        "question": "71. Металлические свойства элементов в группе...",
        "options": ["Усиливаются сверху вниз", "Ослабевают сверху вниз", "Не изменяются"],
        "correct": "Усиливаются сверху вниз"
    },
    {
        "question": "72. Неметаллические свойства в периоде...",
        "options": ["Усиливаются слева направо", "Ослабевают слева направо", "Не изменяются"],
        "correct": "Усиливаются слева направо"
    },
    {
        "question": "73. Атомная орбиталь характеризуется...",
        "options": ["Определенной траекторией движения электрона", "Вероятностью нахождения электрона", "Постоянным радиусом"],
        "correct": "Вероятностью нахождения электрона"
    },
    {
        "question": "74. Волновая функция, описывающая состояние электрона, - это...",
        "options": ["Ψ (Пси)", "Φ (Фи)", "Ω (Омега)"],
        "correct": "Ψ (Пси)"
    },
    {
        "question": "75. Квадрат волновой функции (Ψ²) характеризует...",
        "options": ["Энергию электрона", "Вероятность нахождения электрона", "Спин электрона"],
        "correct": "Вероятность нахождения электрона"
    },
    {
        "question": "76. Что такое электронное облако?",
        "options": ["Графическое изображение орбитали", "Совокупность всех электронов", "Ядро атома"],
        "correct": "Графическое изображение орбитали"
    },
    {
        "question": "77. У какого изотопа водорода нет нейтронов в ядре?",
        "options": ["Протий", "Дейтерий", "Тритий"],
        "correct": "Протий"
    },
    {
        "question": "78. Атом какого элемента всегда имеет валентность II?",
        "options": ["Кислород (O)", "Кальций (Ca)", "Цинк (Zn)"],
        "correct": "Цинк (Zn)"
    },
    {
        "question": "79. Что такое амфотерность?",
        "options": ["Способность проявлять кислотные свойства", "Способность проявлять и основные, и кислотные свойства", "Способность проявлять основные свойства"],
        "correct": "Способность проявлять и основные, и кислотные свойства"
    },
    {
        "question": "80. s-Элементами являются...",
        "options": ["Щелочные и щелочноземельные металлы", "Галогены", "Инертные газы"],
        "correct": "Щелочные и щелочноземельные металлы"
    },
    {
        "question": "81. p-Элементами являются...",
        "options": ["Элементы главных подгрупп III-VIII групп", "Элементы побочных подгрупп", "Лантаноиды"],
        "correct": "Элементы главных подгрупп III-VIII групп"
    },
    {
        "question": "82. f-Элементами являются...",
        "options": ["Уран и торий", "Лантаноиды и актиноиды", "Все радиоактивные элементы"],
        "correct": "Лантаноиды и актиноиды"
    },
    {
        "question": "83. Атомная масса протона примерно равна...",
        "options": ["Массе электрона", "1 а.е.м.", "0 а.е.м."],
        "correct": "1 а.е.м."
    },
    {
        "question": "84. Масса электрона примерно равна...",
        "options": ["1/1840 а.е.м.", "1 а.е.м.", "2 а.е.м."],
        "correct": "1/1840 а.е.м."
    },
    {
        "question": "85. Заряд протона равен...",
        "options": ["0", "+1", "-1"],
        "correct": "+1"
    },
    {
        "question": "86. Заряд электрона равен...",
        "options": ["0", "+1", "-1"],
        "correct": "-1"
    },
    {
        "question": "87. Заряд нейтрона равен...",
        "options": ["0", "+1", "-1"],
        "correct": "0"
    },
    {
        "question": "88. Современная модель атома называется...",
        "options": ["Планетарной", "Квантово-механической", "«Пудинг с изюмом»"],
        "correct": "Квантово-механической"
    },
    {
        "question": "89. Принцип неопределенности Гейзенберга гласит, что...",
        "options": ["Невозможно точно определить заряд электрона", "Невозможно одновременно точно определить координату и импульс частицы", "Электрон может находиться в двух местах одновременно"],
        "correct": "Невозможно одновременно точно определить координату и импульс частицы"
    },
    {
        "question": "90. Что такое вырожденные орбитали?",
        "options": ["Орбитали разной формы", "Орбитали с разной энергией", "Орбитали с одинаковой энергией"],
        "correct": "Орбитали с одинаковой энергией"
    },
    {
        "question": "91. Какой элемент имеет аномально высокую температуру плавления благодаря особой структуре электронных орбиталей?",
        "options": ["Углерод (алмаз)", "Железо (Fe)", "Ртуть (Hg)"],
        "correct": "Углерод (алмаз)"
    },
    {
        "question": "92. Явление испускания электронов веществом под действием света называется...",
        "options": ["Радиоактивность", "Фотоэффект", "Ионизация"],
        "correct": "Фотоэффект"
    },
    {
        "question": "93. Линейчатый спектр атома водорода объяснила модель атома...",
        "options": ["Резерфорда", "Бора", "Томсона"],
        "correct": "Бора"
    },
    {
        "question": "94. Основное состояние атома - это...",
        "options": ["Состояние с минимальной энергией", "Возбужденное состояние", "Ионизированное состояние"],
        "correct": "Состояние с минимальной энергией"
    },
    {
        "question": "95. Что такое валентные возможности атома?",
        "options": ["Способность образовывать ионы", "Способность образовывать определенное число химических связей", "Способность проводить ток"],
        "correct": "Способность образовывать определенное число химических связей"
    },
    {
        "question": "96. Что такое степень окисления?",
        "options": ["Реальный заряд атома в молекуле", "Условный заряд атома, вычисленный исходя из предположения об ионном характере связей", "Число связей, образуемых атомом"],
        "correct": "Условный заряд атома, вычисленный исходя из предположения об ионном характере связей"
    },
    {
        "question": "97. Что такое радионуклиды?",
        "options": ["Все изотопы", "Радиоактивные изотопы", "Стабильные изотопы"],
        "correct": "Радиоактивные изотопы"
    },
    {
        "question": "98. Понятие «атом» ввел...",
        "options": ["Демокрит", "Дальтон", "Ломоносов"],
        "correct": "Демокрит"
    },
    {
        "question": "99. Строение ядра атома (протоны, нейтроны) было открыто...",
        "options": ["В XIX веке", "В начале XX века (1910-е гг.)", "В середине XX века (1950-е гг.)"],
        "correct": "В начале XX века (1910-е гг.)"
    },
    {
        "question": "100. Современная теория строения атома основана на...",
        "options": ["Только на теории Бора", "Только на модели Резерфорда", "На квантовой механике"],
        "correct": "На квантовой механике"
    }
]


class Registration(StatesGroup):
    waiting_for_class = State()
    waiting_for_fio = State()


class Quiz(StatesGroup):
    answering_questions = State()


async def init_db():
    async with aiosqlite.connect('bot.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                full_name TEXT,
                class_number INTEGER,
                class_letter TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                question_id INTEGER,
                answer TEXT,
                is_correct INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.commit()


async def get_admin_id():
    try:
        async with aiofiles.open('admin_id.txt', mode='r') as f:
            content = await f.read()
            return int(content.strip())
    except (FileNotFoundError, ValueError):
        return None


async def save_admin_id(admin_id):
    async with aiofiles.open('admin_id.txt', mode='w') as f:
        await f.write(str(admin_id))


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать! Для регистрации введите /register")


@dp.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with aiosqlite.connect('bot.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = await cursor.fetchone()

    if user:
        await message.answer("Вы уже зарегистрированы!")
    else:
        await state.set_state(Registration.waiting_for_class)
        await message.answer("Введите ваш класс (например: 10А):")


@dp.message(Registration.waiting_for_class)
async def process_class(message: types.Message, state: FSMContext):
    class_input = message.text.upper().strip()

    if len(class_input) < 2 or not class_input[:-1].isdigit() or not class_input[-1].isalpha():
        await message.answer("Неверный формат. Введите класс правильно (например: 10А):")
        return

    class_number = int(class_input[:-1])
    class_letter = class_input[-1]

    if not (1 <= class_number <= 11):
        await message.answer("Класс должен быть от 1 до 11. Попробуйте снова:")
        return

    await state.update_data(class_number=class_number, class_letter=class_letter)
    await state.set_state(Registration.waiting_for_fio)
    await message.answer("Теперь введите ваше ФИО:")


@dp.message(Registration.waiting_for_fio)
async def process_fio(message: types.Message, state: FSMContext):
    fio = message.text.strip()

    if fio.lower() == "esp42teach":
        admin_id = message.from_user.id
        await save_admin_id(admin_id)
        await message.answer("Вы назначены администратором!")
        await state.clear()
        return

    user_data = await state.get_data()
    user_id = message.from_user.id

    async with aiosqlite.connect('bot.db') as db:
        await db.execute(
            "INSERT INTO users (user_id, full_name, class_number, class_letter) VALUES (?, ?, ?, ?)",
            (user_id, fio, user_data['class_number'], user_data['class_letter'])
        )
        await db.commit()

    await state.clear()
    await message.answer("Регистрация завершена! Для начала опроса используйте /quiz.")


@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with aiosqlite.connect('bot.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user = await cursor.fetchone()

    if not user:
        await message.answer("Сначала зарегистрируйтесь через /start.")
        return

    selected_questions = random.sample(quiz_questions, 100)
    await state.set_state(Quiz.answering_questions)
    await state.update_data(
        current_question=0,
        answers={},
        quiz_questions=selected_questions,
        user_id=user_id
    )
    await send_question(message, state)


async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_question = data['current_question']
    quiz_questions = data['quiz_questions']

    if current_question >= len(quiz_questions):
        await finish_quiz(message, state)
        return

    question_data = quiz_questions[current_question]

    builder = ReplyKeyboardBuilder()
    for option in question_data["options"]:
        builder.add(types.KeyboardButton(text=option))
    builder.adjust(1)

    await message.answer(
        question_data["question"],
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@dp.message(Quiz.answering_questions)
async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_question = data['current_question']
    answers = data['answers']
    quiz_questions = data['quiz_questions']
    user_id = data['user_id']

    question_data = quiz_questions[current_question]
    user_answer = message.text
    is_correct = user_answer == question_data["correct"]

    answers[current_question] = {
        "question": question_data["question"],
        "user_answer": user_answer,
        "correct_answer": question_data["correct"],
        "is_correct": is_correct
    }

    async with aiosqlite.connect('bot.db') as db:
        await db.execute(
            "INSERT INTO answers (user_id, question_id, answer, is_correct) VALUES (?, ?, ?, ?)",
            (user_id, current_question, user_answer, 1 if is_correct else 0)
        )
        await db.commit()

    if current_question < len(quiz_questions) - 1:
        await state.update_data(
            current_question=current_question + 1,
            answers=answers
        )
        await send_question(message, state)
    else:
        await state.update_data(answers=answers)
        await finish_quiz(message, state)


async def finish_quiz(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answers = data['answers']
    correct_count = sum(1 for answer in answers.values() if answer["is_correct"])
    total_questions = len(answers)
    result_text = "Опрос завершен!\n\n"
    o = 1
    for i, answer in answers.items():
        result_text += f"{answer['question']}\n"
        result_text += f"Ваш ответ: {answer['user_answer']}\n"
        result_text += f"Правильный ответ: {answer['correct_answer']}\n"
        result_text += "✓ Верно\n" if answer["is_correct"] else "✗ Неверно\n"
        result_text += "\n"
        if o == 100:
            result_text += f"Ваш результат: {correct_count}/{total_questions}\n\nВы можете запустить квест снова /quiz"
        if o % 13 == 0:
            await message.answer(result_text, reply_markup=types.ReplyKeyboardRemove())
            result_text = ''
            o += 1
    admin_id = await get_admin_id()
    if admin_id:
        async with aiosqlite.connect('bot.db') as db:
            cursor = await db.execute(
                "SELECT full_name, class_number, class_letter FROM users WHERE user_id=?",
                (data['user_id'],)
            )
            user = await cursor.fetchone()

        if user:
            full_name, class_number, class_letter = user
            await bot.send_message(
                admin_id,
                f"Пользователь {class_number}{class_letter} {full_name} "
                f"завершил опрос с результатом {correct_count}/{total_questions}."
            )

    await state.clear()


@dp.message(Command("users"))
async def cmd_users(message: types.Message):
    admin_id = await get_admin_id()
    if not admin_id or message.from_user.id != admin_id:
        await message.answer("Эта команда только для администратора.")
        return

    async with aiosqlite.connect('bot.db') as db:
        cursor = await db.execute(
            "SELECT full_name, class_number, class_letter FROM users ORDER BY class_number, class_letter, full_name"
        )
        users = await cursor.fetchall()

    if not users:
        await message.answer("Нет зарегистрированных пользователей.")
        return

    response = "Список пользователей:\n"
    for user in users:
        full_name, class_number, class_letter = user
        response += f"{class_number}{class_letter} - {full_name}\n"

    await message.answer(response)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())