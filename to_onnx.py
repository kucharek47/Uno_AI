import torch
from bot import siec_neuronowa


def konwertuj_do_onnx():
    max_graczy = 5
    wielkosc_wejscia = 170 + (max_graczy - 1) * 3
    wielkosc_wyjscia = 63 + max_graczy

    print("Inicjalizacja modelu...")
    model = siec_neuronowa(wielkosc_wejscia, wielkosc_wyjscia)

    sciezka_pth = "model_uno_v10.pth"
    print(f"Wczytywanie wag z pliku {sciezka_pth}...")
    punkt_kontrolny = torch.load(sciezka_pth, map_location=torch.device('cpu'), weights_only=False)

    model.load_state_dict(punkt_kontrolny['model_state_dict'])

    model.eval()

    dummy_input = torch.randn(1, wielkosc_wejscia)

    sciezka_onnx = "model_uno_v10.onnx"
    print(f"Rozpoczynam konwersję do {sciezka_onnx}...")

    torch.onnx.export(
        model,
        dummy_input,
        sciezka_onnx,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['stan'],
        output_names=['wyjscie'],
        dynamic_axes={
            'stan': {0: 'batch_size'},
            'wyjscie': {0: 'batch_size'}
        }
    )

    print("--------------------------------------------------")
    print(f"✅ SUKCES! Model został przekonwertowany.")
    print(f"Teraz skopiuj plik '{sciezka_onnx}' na swoje Orange Pi 5 do folderu z serwerem.")


if __name__ == "__main__":
    konwertuj_do_onnx()