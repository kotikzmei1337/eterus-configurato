import math
import flet as ft

# База данных характеристик шинопроводов
CHARACTERISTICS = {
    "AL": {
        400: (0.129, 0.254),
        630: (0.093, 0.048),
        800: (0.076, 0.023),
        1000: (0.062, 0.018),
        1250: (0.046, 0.016),
        1600: (0.035, 0.012),
        2000: (0.028, 0.010),
        2500: (0.021, 0.008),
        3200: (0.017, 0.007),
        4000: (0.014, 0.006),
        5000: (0.011, 0.004),
        6300: (0.009, 0.003),
    },
    "CU": {
        800: (0.044, 0.020),
        1000: (0.044, 0.020),
        1250: (0.035, 0.017),
        1600: (0.028, 0.015),
        2000: (0.023, 0.010),
        2500: (0.016, 0.006),
        3200: (0.011, 0.005),
        4000: (0.009, 0.005),
        5000: (0.008, 0.004),
        6300: (0.006, 0.003),
    }
}


def main(page: ft.Page):
    # Настройки страницы
    page.title = "Конфигуратор ЭТЕРУС"
    page.window.width = 450
    page.window.height = 750
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # Поля ввода
    dd_material = ft.Dropdown(
        label="Материал",
        value="AL",
        options=[ft.dropdown.Option("AL"), ft.dropdown.Option("CU")],
        on_select=lambda e: update_currents(e.control.value)  # Работает в новых версиях Flet
    )

    dd_in = ft.Dropdown(
        label="Номинальный ток Iн (А)",
        value="400",
        options=[ft.dropdown.Option(str(x)) for x in CHARACTERISTICS["AL"].keys()]
    )

    txt_un = ft.TextField(label="Напряжение Uн (В)", value="380", keyboard_type=ft.KeyboardType.NUMBER)
    txt_boxes = ft.TextField(label="Кол-во коробок (шт)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
    txt_length = ft.TextField(label="Длина трассы L (м)", value="80", keyboard_type=ft.KeyboardType.NUMBER)
    txt_ip = ft.TextField(label="Ток нагрузки Iр (А)", value="400", keyboard_type=ft.KeyboardType.NUMBER)
    txt_cos = ft.TextField(label="Коэффициент cos φ", value="0.95", keyboard_type=ft.KeyboardType.NUMBER)

    # Элементы вывода результатов
    lbl_k = ft.Text(value="-", weight=ft.FontWeight.BOLD)
    lbl_sin = ft.Text(value="-")
    lbl_z = ft.Text(value="-")
    lbl_du_v = ft.Text(value="-", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    lbl_du_pct = ft.Text(value="-", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    lbl_error = ft.Text(value="", color=ft.Colors.RED_400, size=13)

    def update_currents(mat):
        """Обновление токов при смене материала."""
        currents = list(CHARACTERISTICS[mat].keys())
        dd_in.options = [ft.dropdown.Option(str(x)) for x in currents]
        dd_in.value = str(currents[0])
        page.update()

    def calculate(e):
        """Расчет падения напряжения."""
        lbl_error.value = ""
        try:
            mat = dd_material.value
            in_val = int(dd_in.value)
            un_val = float(txt_un.value.replace(",", "."))
            n_boxes = int(txt_boxes.value)
            l_val = float(txt_length.value.replace(",", "."))
            ip_val = float(txt_ip.value.replace(",", "."))
            cos_phi = float(txt_cos.value.replace(",", "."))

            if not (0 <= cos_phi <= 1):
                lbl_error.value = " Ошибка: cos φ должен быть от 0 до 1"
                page.update()
                return

            if n_boxes < 0 or l_val < 0 or ip_val < 0 or un_val <= 0:
                lbl_error.value = " Ошибка: значения должны быть положительными"
                page.update()
                return

            # Вычисление коэффициента k
            k = 1.0 if n_boxes == 0 else (1 + n_boxes) / (2 * n_boxes)

            # sin φ
            sin_phi = math.sqrt(1 - cos_phi**2)

            # R и X из таблицы
            r_val, x_val = CHARACTERISTICS[mat][in_val]

            # Полное сопротивление Z
            z_val = r_val * cos_phi + x_val * sin_phi

            # dU (Вольт) = k * L * Ip * 1.73 * Z * 0.001
            du_volts = k * l_val * ip_val * 1.73 * z_val * 0.001

            # dU (%) = (dU / Un) * 100
            du_percent = (du_volts / un_val) * 100

            # Отображение результатов
            lbl_k.value = f"{k:.4f}"
            lbl_sin.value = f"{sin_phi:.4f}"
            lbl_z.value = f"{z_val:.5f} мОм/м"
            lbl_du_v.value = f"{du_volts:.2f} В"
            lbl_du_pct.value = f"{du_percent:.2f} %"

        except ValueError:
            lbl_error.value = " Ошибка: проверьте корректность данных!"

        page.update()

    # Сборка интерфейса
    page.add(
        ft.Column(
            [
                ft.Text(
                    "Расчет падения напряжения\n«Конфигуратор ЭТЕРУС»",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Divider(),
                dd_material,
                dd_in,
                txt_un,
                txt_boxes,
                txt_length,
                txt_ip,
                txt_cos,
                ft.ElevatedButton(
                    "РАССЧИТАТЬ",
                    on_click=calculate,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                    width=400,
                    height=45,
                ),
                lbl_error,
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row([ft.Text("Коэффициент (k):"), lbl_k], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([ft.Text("sin φ:"), lbl_sin], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([ft.Text("Z (R·cos + X·sin):"), lbl_z], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Divider(),
                                ft.Row([ft.Text("Падение dU (В):", weight=ft.FontWeight.BOLD), lbl_du_v], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([ft.Text("Падение dU (%):", weight=ft.FontWeight.BOLD), lbl_du_pct], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ]
                        ),
                        padding=15,
                    )
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)