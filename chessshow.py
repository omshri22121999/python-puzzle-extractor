import chess.pgn
import chess.svg
import re
import chess
import tkinter
import tkinter.messagebox as messagebox
import io
import json
import os
import sys
import PIL.Image
import PIL.ImageTk
import cairosvg

pgn = open("./tactics.pgn")

pgn_data = []

game = 1

while game != None:
    game = chess.pgn.read_game(pgn)
    if game != None:
        data = {}
        data["Text"] = game.headers["Black"] + "-" + game.headers["White"]
        data["FEN"] = game.headers["FEN"]
        data["Moves"] = list(game.mainline_moves())
        pgn_data.append(data)

if len(pgn_data) == 0:
    print("No Tactics Present!")
    sys.exit()

i = 0
j = 0

chessboard_game = chess.Board(pgn_data[i]["FEN"])
window = tkinter.Tk()
input_frame = tkinter.Frame(window)

window.title("Chess Puzzle Show")

head = tkinter.Label(window, text="Problem #" + str(i + 1), font=("Arial Bold", 30))
game = tkinter.Label(window, text=pgn_data[i]["Text"], font=("Arial Bold", 15))
suggest = tkinter.Label(
    input_frame,
    text="Enter your move in UCI format (eg. f8g8) : ",
    font=("Arial Bold", 10),
)

input_move = tkinter.Entry(input_frame)

head.grid(column=0, row=0)
game.grid(column=0, row=1)
input_frame.grid(column=0, row=4)
suggest.pack(side=tkinter.LEFT)
input_move.pack(side=tkinter.LEFT)

chessboard_game.push(pgn_data[i]["Moves"][j])

svg_img = chess.svg.board(
    board=chessboard_game, lastmove=pgn_data[i]["Moves"][j], size=600
)
png_img = cairosvg.svg2png(bytestring=svg_img)
im = PIL.Image.open(io.BytesIO(png_img))
photo = PIL.ImageTk.PhotoImage(im)

img = tkinter.Label(window, image=photo, text=pgn_data[i]["Text"])

img.grid(column=0, row=2, padx=20, pady=20)

j += 1

print(len(pgn_data[i]["Moves"]))


def prev_comm():
    global i
    if i > 0:
        i -= 1
        j = 0

        chessboard_game = chess.Board(pgn_data[i]["FEN"])

        head["text"] = "Problem #" + str(i + 1)
        game["text"] = pgn_data[i]["Text"]

        chessboard_game.push(pgn_data[i]["Moves"][j])

        svg_img = chess.svg.board(
            board=chessboard_game, lastmove=pgn_data[i]["Moves"][j], size=600
        )
        png_img = cairosvg.svg2png(bytestring=svg_img)
        im = PIL.Image.open(io.BytesIO(png_img))
        photo = PIL.ImageTk.PhotoImage(im)
        img.configure(image=photo)
        img.image = photo
        img["text"] = pgn_data[i]["Text"]

        j += 1


def next_comm():
    global i
    if i < len(pgn_data) - 1:
        i += 1
        j = 0

        chessboard_game = chess.Board(pgn_data[i]["FEN"])

        head["text"] = "Problem #" + str(i + 1)
        game["text"] = pgn_data[i]["Text"]

        chessboard_game.push(pgn_data[i]["Moves"][j])

        svg_img = chess.svg.board(
            board=chessboard_game, lastmove=pgn_data[i]["Moves"][j], size=600
        )
        png_img = cairosvg.svg2png(bytestring=svg_img)
        im = PIL.Image.open(io.BytesIO(png_img))
        photo = PIL.ImageTk.PhotoImage(im)
        img.configure(image=photo)
        img.image = photo
        img["text"] = pgn_data[i]["Text"]

        j += 1


def enter_move(event=None):
    global j
    if j < len(pgn_data[i]["Moves"]):
        move = input_move.get()
        if move.strip() == pgn_data[i]["Moves"][j].uci():
            if j != len(pgn_data[i]["Moves"]) - 1:
                chessboard_game.push(pgn_data[i]["Moves"][j])
                frm_sq = pgn_data[i]["Moves"][j].from_square
                to_sq = pgn_data[i]["Moves"][j].to_square
                j += 1
                chessboard_game.push(pgn_data[i]["Moves"][j])
                svg_img = chess.svg.board(
                    board=chessboard_game,
                    arrows=[chess.svg.Arrow(tail=frm_sq, head=to_sq)],
                    lastmove=pgn_data[i]["Moves"][j],
                    size=600,
                )
                png_img = cairosvg.svg2png(bytestring=svg_img)
                im = PIL.Image.open(io.BytesIO(png_img))
                photo = PIL.ImageTk.PhotoImage(im)
                img.configure(image=photo)
                img.image = photo
                img["text"] = pgn_data[i]["Text"]
                j += 1
            else:
                chessboard_game.push(pgn_data[i]["Moves"][j])
                frm_sq = pgn_data[i]["Moves"][j].from_square
                to_sq = pgn_data[i]["Moves"][j].to_square
                svg_img = chess.svg.board(
                    board=chessboard_game,
                    arrows=[chess.svg.Arrow(tail=frm_sq, head=to_sq)],
                    size=600,
                )
                png_img = cairosvg.svg2png(bytestring=svg_img)
                im = PIL.Image.open(io.BytesIO(png_img))
                photo = PIL.ImageTk.PhotoImage(im)
                img.configure(image=photo)
                img.image = photo
                img["text"] = pgn_data[i]["Text"]
                messagebox.showinfo("Congratulations", "You've completed the puzzle!")
                j += 1
        else:
            messagebox.showerror(
                "Wrong Answer", "Your answer is wrong, please try again"
            )
    else:
        messagebox.showinfo(
            "Completed", "You've completed the puzzle, please move on to the next!",
        )

    input_move.delete(0, len(input_move.get()))


prev_b = tkinter.Button(window, command=prev_comm, text="Back", height=3, width=9)

prev_b.grid(column=0, row=5, padx=20, pady=20, sticky="W")

next_b = tkinter.Button(window, command=next_comm, text="Next", height=3, width=9)

next_b.grid(column=0, row=5, padx=20, pady=20, sticky="E")

enter = tkinter.Button(input_frame, command=enter_move, text="Enter", height=1, width=6)

window.bind("<Return>", enter_move)

enter.pack(
    side=tkinter.RIGHT, padx=20, pady=20,
)

window.mainloop()
