from car_plate_detection import *
from os.path import exists
from time import perf_counter

if __name__ == "__main__":

    # path_to_file = 'dataset/car1.mp4'

    # if not exists(path_to_file):
    #     raise FileNotFoundError(f"{path_to_file} does not exist")
    # cap = cv2.VideoCapture(path_to_file)
    # ret, current_frame = cap.read()

    # w = int(cap.get(3))
    # h = int(cap.get(4))

    # fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    # out = cv2.VideoWriter('output2.mp4', fourcc, 20, (w, h), isColor=True)

    # t1 = perf_counter()
    # while(cap.isOpened()):

    #     result = detect_number(current_frame)[1]
    #     out.write(result)
    #     key = cv2.waitKey(20)
    #     if key == ord('q'):
    #         break
    #     ret, current_frame = cap.read()
    #     if not ret:
    #         break

    # cap.release()
    # out.release()
    # cv2.destroyAllWindows()
    # print(f"{(perf_counter() - t1):.2f} s")

    # code = "AD 081 FD"
    # results = get_countries_from_license_plate_code(code)
    # for r in results:
    #     print(r[0], r[1])

    img = cv2.imread('dataset/nd.png')
    result = detect_number(img)[0]

    cv2.imwrite("nazwa.png", result)
