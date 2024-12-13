import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QFormLayout, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import datetime
from lark import Lark, Transformer
from lark.tree import Tree

# Código de conversión de monedas
conversion_rates = {
    "USD": {"EUR": 0.85, "JPY": 110.0, "GBP": 0.73, "CAD": 1.25, "USD":1, "LPS": 24.62},
    "EUR": {"USD": 1.18, "JPY": 130.0, "GBP": 0.87, "CAD": 1.49, "EUR":1, "LPS": 26.85},
    "JPY": {"USD": 0.009, "EUR": 0.0077, "GBP": 0.0062, "CAD": 0.011, "JPY":1, "LPS": 0.17},
    "GBP": {"USD": 1.27, "EUR": 1.16, "JPY": 184.59, "CAD": 1.71, "GBP":1, "LPS": 31.23},
    "CAD": {"USD": 0.74, "EUR": 0.68, "JPY": 108.11, "GBP": 0.59, "CAD":1, "LPS": 18.29},
    "LPS": {"USD": 0.041, "EUR": 0.037, "JPY": 5.91, "GBP": 0.032, "CAD":0.055, "LPS":1}
}

conversion_grammar = """
    ?start: AMOUNT CURRENCY "to" CURRENCY
          | AMOUNT CURRENCY "TO" CURRENCY
          | AMOUNT CURRENCY "a" CURRENCY
          | AMOUNT CURRENCY "A" CURRENCY

    AMOUNT: /[0-9]+(\.[0-9]+)?/
    CURRENCY: /[A-Za-z]{3}/

    %import common.WS_INLINE
    %ignore WS_INLINE
"""

class ConvertCurrency(Transformer):
    def start(self, items):
        amount = float(items[0])
        from_currency = items[1].upper()
        to_currency = items[2].upper()
        rate = conversion_rates[from_currency][to_currency]
        converted_amount = amount * rate
        tree = Tree('conversion', [Tree('amount', [amount]), Tree('from_currency', [from_currency]), Tree('to_currency', [to_currency]), Tree('converted_amount', [converted_amount])])
        return tree

conversion_parser = Lark(conversion_grammar, parser='lalr', transformer=ConvertCurrency())
convert_currency = conversion_parser.parse

# Código de la interfaz
class CurrencyChartApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Convertidor de Monedas y Gráfico')
        self.setGeometry(100, 100, 800, 700)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        # Sección del gráfico y el select de moneda
        self.chart_canvas = FigureCanvas(plt.figure(figsize=(8, 5)))
        layout.addWidget(self.chart_canvas)

        self.currency_label = QLabel('Selecciona una moneda:')
        layout.addWidget(self.currency_label)

        self.currency_combo = QComboBox()
        self.currency_combo.addItems(['USD', 'EUR', 'JPY', 'GBP', 'CAD', 'LPS'])
        self.currency_combo.currentIndexChanged.connect(self.update_chart)
        layout.addWidget(self.currency_combo)

        self.to_currency_combo_chart = QComboBox()
        self.to_currency_combo_chart.addItems(['USD', 'EUR', 'JPY', 'GBP', 'CAD', 'LPS'])
        self.to_currency_combo_chart.currentIndexChanged.connect(self.update_chart)
        layout.addWidget(QLabel('Moneda de destino:'))
        layout.addWidget(self.to_currency_combo_chart)

        # Sección de conversión de monedas
        self.input_lineedit = QLineEdit()
        self.show_button = QPushButton('Convertir')
        self.result_label = QLabel()

        self.show_button.clicked.connect(self.show_text)

        layout.addWidget(QLabel('Ingresa la expresión de conversión (ejemplo: 10 USD a EUR):'))
        layout.addWidget(self.input_lineedit)
        layout.addWidget(self.show_button)
        layout.addWidget(self.result_label)

        # Sección para el monto y selectores de origen y destino
        self.amount_input = QLineEdit()
        self.from_currency_combo = QComboBox()
        self.to_currency_combo = QComboBox()

        section_layout = QFormLayout()
        section_layout.addRow(QLabel('Monto:'), self.amount_input)
        section_layout.addRow(QLabel('Moneda de origen:'), self.from_currency_combo)
        section_layout.addRow(QLabel('Moneda de destino:'), self.to_currency_combo)

        self.from_currency_combo.addItems(conversion_rates.keys())
        self.to_currency_combo.addItems(conversion_rates.keys())

        self.show_button_section2 = QPushButton('Convertir')
        self.result_label_section2 = QLabel()

        self.show_button_section2.clicked.connect(self.show_text_section2)

        section_layout.addRow(self.show_button_section2)
        section_layout.addWidget(self.result_label_section2)

        layout.addLayout(section_layout)

        self.central_widget.setLayout(layout)

        # Datos para el gráfico
        self.dates = [
            datetime.date(2023, 8, 1),
            datetime.date(2023, 8, 2),
            datetime.date(2023, 8, 3),
            datetime.date(2023, 8, 4),
            datetime.date(2023, 8, 5),
            datetime.date(2023, 8, 6),
            datetime.date(2023, 8, 7),
            datetime.date(2023, 8, 8),
            datetime.date(2023, 8, 9),
            datetime.date(2023, 8, 10)
        ]

        # Valores de moneda de ejemplo
        self.currency_values = {
            'USD': [1.0, 1.3, 1.5, 1.6, 1.0, 1.2, 1.1, 1.3, 1.7, 1.0],
            'EUR': [0.85, 0.9, 0.92, 0.88, 0.87, 0.84, 0.83, 0.85, 0.81, 0.80],
            'JPY': [110.0, 108.0, 105.0, 102.0, 100.0, 98.0, 95.0, 92.0, 90.0, 88.0],
            'GBP': [0.73, 0.72, 0.71, 0.74, 0.77, 0.75, 0.76, 0.78, 0.80, 0.82],
            'CAD': [1.25, 1.22, 1.18, 1.15, 1.12, 1.10, 1.08, 1.05, 1.03, 1.0],
            'LPS': [24.6300, 24.6312, 24.6500, 24.5995, 24.4094, 24.4349, 24.5776, 24.5875, 24.5959, 24.5956]
        }
        self.update_chart()

    def show_text(self):
        input_text = self.input_lineedit.text()
        try:
            result = convert_currency(input_text)
            self.result_label.setText(f'Árbol Sintáctico:\n{result.pretty()}')
        except Exception as e:
            self.result_label.setText(f'Error al procesar la expresión: {e}')

    def show_text_section2(self):
        try:
            amount = float(self.amount_input.text())
            from_currency = self.from_currency_combo.currentText()
            to_currency = self.to_currency_combo.currentText()
            rate = conversion_rates[from_currency][to_currency]
            converted_amount = amount * rate
            self.result_label_section2.setText(f'Conversión: {amount} {from_currency} = {converted_amount:.2f} {to_currency}')
        except Exception as e:
            self.result_label_section2.setText(f'Error al procesar la expresión: {e}')

    def update_chart(self):
        selected_currency = self.currency_combo.currentText()
        to_currency = self.to_currency_combo_chart.currentText()  # Nueva divisa seleccionada

        # Calcula la tasa de cambio entre las dos divisas seleccionadas
        rate = conversion_rates[selected_currency][to_currency]

        # Calcula el monto usando la tasa de cambio
        values = [rate * value for value in self.currency_values[selected_currency]]

        if values:
            self.chart_canvas.figure.clear()
            ax = self.chart_canvas.figure.add_subplot(1, 1, 1)
            ax.plot(self.dates, values, marker='o')
            ax.set_xticks(self.dates)
            ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in self.dates], rotation=45)
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Tasa de Cambio')
            ax.set_title(f'Tasa de Cambio {selected_currency} a {to_currency} vs Fecha')
            ax.grid(True)

            plt.subplots_adjust(bottom=0.4)  # Ajusta este valor según sea necesario

            self.chart_canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CurrencyChartApp()
    main_window.show()
    sys.exit(app.exec_())
