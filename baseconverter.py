import PySimpleGUI as sg
sg.theme("Gray Gray Gray")
layout = [[sg.Text("Base Converter Program (DON\'T INPUT FLOATS)         Base Input V")],
        [sg.Text("Input:"), sg.Input(key="input", pad=(11, 0)), sg.Input(key="frombasein", size=2)],
        [sg.Text("Output:"), sg.Input(key="output", disabled=True, pad=0), sg.Input(key="tobasein", size=2, pad=(16, 0))],
        [sg.Button("60"), sg.Button("Close")],
        [sg.Text("Loading Bays for Symbols:")],
        [sg.Multiline(key="symbolsin", size=(24,6), default_text="[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]")]]
window = sg.Window("Base Converter", layout)
while True:
    event, values = window.read()
    if event == "Close":
        break
window.close()
print("You may now exit the window.")
