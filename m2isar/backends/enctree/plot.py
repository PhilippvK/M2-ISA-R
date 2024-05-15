
import matplotlib.pyplot as plt
import numpy as np

def plot_space(outpath, data_all):
    fig, ax = plt.subplots(figsize=(16,4))

    num_rows = len(data_all)

    SHIFT = 0.3
    HEIGHT = 0.2

    for i, data_ in enumerate(data_all):
        bits, field_str, data = data_
        print("i", i)
        print("data", data)

        x = 0
        active_rect = None
        for width, value, label, active in data:
            rect = plt.Rectangle((x, SHIFT * i), value, HEIGHT,
                             facecolor="black", alpha=0.3)
            ax.add_patch(rect)
            rect_ = plt.Rectangle((x, SHIFT * i), width, HEIGHT,
                             facecolor="black", fill=None, lw=1.5)
            ax.add_patch(rect_)
            rx, ry = rect_.get_xy()
            cx = rx + rect_.get_width()/2.0
            cy = ry + rect_.get_height()/2.0

            # ax.annotate(label, (cx, cy), color="red" if active else "black", weight="bold",
            #             fontsize=7, ha="center", va="center")
            rotation = 90 if width < 10 else 0
            ax.text(cx, cy, label, color="red" if active else "black",
                    ha="center", va="center", rotation=rotation, size=7)
            x += width

            if active:
                active_rect = rect_

        if active_rect:
            rx, ry = active_rect.get_xy()
            rw = active_rect.get_width()
            rh = active_rect.get_height()
            ax.plot([rx, 0], [ry+rh, SHIFT * (i + 1)], color="gray")
            ax.plot([rx+rw, 100], [ry+rh, SHIFT * (i + 1)], color="gray")
        ax.text(-100/40, HEIGHT / 2 + SHIFT * i, f"{bits}-bit\n{field_str}",
                    ha="center", va="center", rotation=90, size=7)

        ### x = 0
        ### active_rect = None
        ### for width, value, label, active in data2:
        ###     rect = plt.Rectangle((x, 0.3), value, 0.2,
        ###                      facecolor="black", alpha=0.3)
        ###     ax.add_patch(rect)
        ###     rect_ = plt.Rectangle((x, 0.3), width, 0.2,
        ###                      facecolor="black", fill=None, lw=1.5)
        ###     ax.add_patch(rect_)
        ###     rx, ry = rect_.get_xy()
        ###     cx = rx + rect_.get_width()/2.0
        ###     cy = ry + rect_.get_height()/2.0

        ###     #ax.annotate(label, (cx, cy), color="black", weight="bold",
        ###     #            fontsize=7, ha="center", va="center", rotate=90)
        ###     ax.text(cx, cy, label, color="red" if active else "black",
        ###             ha="center", va="center", rotation=90, size=7)
        ###     x += width

        ###     if active:
        ###         active_rect = rect_

        ### rx, ry = active_rect.get_xy()
        ### rw = active_rect.get_width()
        ### rh = active_rect.get_height()
        ### ax.plot([rx, 0], [ry+rh, 0.6], color="gray")
        ### ax.plot([rx+rw, 100], [ry+rh, 0.6], color="gray")
        ### ax.text(-100/40, 0.4, "30-bit",
        ###             ha="center", va="center", rotation=90, size=7)

        ### x = 0
        ### for width, value, label in data3:
        ###     rect = plt.Rectangle((x, 0.6), value, 0.2,
        ###                      facecolor="blue", alpha=0.3)
        ###     ax.add_patch(rect)
        ###     rect_ = plt.Rectangle((x, 0.6), width, 0.2,
        ###                      facecolor="black", fill=None, lw=1.5)
        ###     ax.add_patch(rect_)
        ###     rx, ry = rect_.get_xy()
        ###     cx = rx + rect_.get_width()/2.0
        ###     cy = ry + rect_.get_height()/2.0

        ###     #ax.annotate(label, (cx, cy), color="black", weight="bold",
        ###     #            fontsize=7, ha="center", va="center", rotate=90)
        ###     ax.text(cx, cy, label,
        ###             ha="center", va="center", rotation=90, size=7)
        ###     x += width

        ### ax.text(-100/40, 0.7, "25-bit",
        ###             ha="center", va="center", rotation=90, size=7)

    ax.set_ylim(-0.1, 1.1)
    ax.set_xlim(-100/20, 100 + 100/20)

    plt.savefig(outpath)
