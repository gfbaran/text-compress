import numpy as np
from PIL import Image
import tkinter as tk
import os
from tkinter import filedialog, messagebox


class LZW:
    def __init__(self):
        self.dictionary_size = 256
        self.dictionary = {chr(i): i for i in range(self.dictionary_size)}

    def compress(self, uncompressed):
        dict_size = self.dictionary_size
        dictionary = self.dictionary.copy()
        w = ""
        result = []

        for c in uncompressed:
            wc = w + c
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = dict_size
                dict_size += 1
                w = c

        if w:
            result.append(dictionary[w])

        return result

    def decompress(self, compressed):
        dict_size = self.dictionary_size
        dictionary = {i: chr(i) for i in range(dict_size)}
        result = []
        w = chr(compressed.pop(0))
        result.append(w)

        for k in compressed:
            if k in dictionary:
                entry = dictionary[k]
            elif k == dict_size:
                entry = w + w[0]
            else:
                raise ValueError(f'Geçersiz sıkıştırılmış kod: {k}')

            result.append(entry)
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
            w = entry

        return "".join(result)


class LZWGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LZW Sıkıştırma Aracı")
        self.lzw = LZW()

        self.label = tk.Label(root, text="Bir dosya seçin:")
        self.label.pack()

        self.select_button = tk.Button(root, text="Dosya Seç", command=self.select_file)
        self.select_button.pack()

        self.compress_button = tk.Button(root, text="Sıkıştır", command=self.compress_file)
        self.compress_button.pack()

        self.decompress_button = tk.Button(root, text="Aç", command=self.decompress_file)
        self.decompress_button.pack()

        self.file_path = ""

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Tüm Dosyalar", "*.*")])
        if self.file_path:
            self.label.config(text=f"Seçilen Dosya: {self.file_path}")


    def compress_file(self):
        if not self.file_path:
            messagebox.showerror("Hata", "Önce bir dosya seçmelisiniz!")
            return

        try:
            with open(self.file_path, "r") as file:
                data = file.read()

            compressed_data = self.lzw.compress(data)
            output_path = self.file_path + ".lzw"

            # Dosyanın kaydedileceği dizini kontrol et ve oluştur
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            np.save(output_path, compressed_data)

            print("Sıkıştırılmış dosya kaydedildi:", output_path)
            messagebox.showinfo("Başarılı", f"Dosya sıkıştırıldı: {output_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Sıkıştırma işlemi başarısız: {str(e)}")

    def decompress_file(self):
        if not self.file_path.endswith(".lzw.npy"):
            messagebox.showerror("Hata", "Geçerli bir sıkıştırılmış dosya seçmelisiniz!")
            return

        compressed_data = np.load(self.file_path, allow_pickle=True).tolist()
        decompressed_data = self.lzw.decompress(compressed_data)
        output_path = self.file_path.replace(".lzw", "_decompressed.txt")

        with open(output_path, "w") as file:
            file.write(decompressed_data)

        messagebox.showinfo("Başarılı", f"Dosya açıldı: {output_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = LZWGUI(root)
    root.mainloop()
