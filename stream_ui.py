from random import sample
import tkinter as tk
import sounddevice as sd
from matplotlib.pyplot import text
import numpy as np
from threading import Thread, Event

class StreamThread(Thread):
    def __init__(self):
        super().__init__()
        self.dispositivo_input= 2
        self.dispositivo_output=4
        self.tamano_bloque=5500
        self.canales=1
        self.tipo_dato= np.int16
        self.latencia="high"
        self.frecuencia_muestreo=44100

    def callback_stream(self, indata, outdata, frames, time, status):
        global app
        app.etiqueta_valor_estado["text"]="Grabando"
        #Obtener frecuencia fundamental
        periodo_muestreo = 1.0/44100
        def callback_stream(indata, outdata, frames, time, status):
            data = indata[:,0]
            transformada = np.fft.rfft(data)
            frecuencias = np.fft.rfftfreq(len(data), periodo_muestreo)
            print("Frecuencia fundamental: ", frecuencias[np.argmax(np.abs(transformada))])

    try:
        with sd.Stream(
            device=(), #elegir dispositivo de audio de entrada y salida, dejar vacio toma los defaults
            blocksize=11025, #0 es que la tarjeta de sonido decide el mejor tamañom es posible que sea variable
            samplerate=44100,
            channels=1,
            dtype = np.int16,
            latency = 'low', 
            callback = callback_stream
        ):
            print('Presiona tecla Enter para salir')
            input()

    except Exception as e:
        print(str(e))
        #Actualizar etiqueta valor ff
        
        return

    def run (self):
        try:
            self.event=Event()
            with sd.Stream(
                device=(self.dispositivo_input, self.dispositivo_output),
                blocksize=self.tamano_bloque, 
                samplerate=self.frecuencia_muestreo, 
                channels=self.canales, 
                dtype=self.tipo_dato, 
                latency=self.latencia, 
                callback=self.callback_stream

            ) as self.stream:
                self.event.wait()

        except Exception as e:
            print(str(e))

#Heredamos de Tk para hcaer una ventana
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        #Establecer titulo de la ventana
        self.title("Aplicacioón de audio")
        #Establecemos tamaño
        self.geometry("400x300")

        boton_iniciar= tk.Button(self, width=20, text="iniciar grabación", command=lambda: self.click_boton_iniciar())
        boton_iniciar.grid(column=0, row=0)

        boton_detener= tk.Button(self, width=20, text="Detener grabación", command=lambda: self.click_boton_iniciar())
        boton_detener.grid(column=1, row=0)

        etiqueta_estado= tk.Label(text="Estado: ")
        etiqueta_estado.grid(column=0, row=1)

        self.etiqueta_valor_estado= tk.Label(text="-")
        self.etiqueta_valor_estado.grid(column=1, row=1)

        etiqueta_frecuencia_fundamenta = tk.Label(text = "Frencuencia fundamental: ")
        etiqueta_frecuencia_fundamenta.grid(column=0, row=2)

        self.etiqueta_valor_ff = tk.Label(text = "-")
        self.etiqueta_valor_ff.grid(column=1, row=2)

        self.stream_thread= StreamThread()

    def click_boton_detener(self):
        if self.stream_thread.is_alive():
            self.etiqueta_valor_estado["text"]="Grabación detenida"
            self.stream_thread.stream.abort()
            self.stream_thread.event.set()
            self.stream_thread.join()

    def click_boton_iniciar(self):
        if self.stream_thread.is_alive():
            self.stream_thread.daemon= True 
            self.stream_thread.start()
            

app=App()
def main():
    global app
    app.mainloop()

if __name__ == "__main__":
    main()
