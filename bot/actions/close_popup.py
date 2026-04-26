import time

close_popup_list_template = [
  "assets/template/x_1.png",
  "assets/template/x_2.png",
  "assets/template/x_3.png",
  "assets/template/back_1.png",
  "assets/template/slt.png"
]

def close_popup(adb):
  for index in range(len(close_popup_list_template)):
    loc = adb.find(close_popup_list_template[index], threshold=0.9)
    if loc is not None:
      adb.click(*loc)
      time.sleep(0.6)
      print("Close popup success!")
      return
  
  print("Don't have any popup appear!")