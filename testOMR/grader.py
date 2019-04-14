# import the necessary packages
import imutils.perspective
from imutils import contours
from .transform import four_point_transform
import numpy as np
import argparse
import imutils
import cv2

def grading(img):

    circleRadius = 10;
    MARKED_COUNT = 120;

    answer = [0, 1, 2, 3, 3, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4, 0, 1, 2, 3, 4];

    #image = cv2.imread("C:\\Users\\xSzy\\Downloads\\rsz_testimg4.jpg");
    image = cv2.imread(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY);

    blurred = cv2.GaussianBlur(gray, (5, 5), 0);
    edged = cv2.Canny(blurred, 75, 200);

    # find contours in the edge map, then initialize
    # the contour that corresponds to the document
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    docCnt = None

    if len(cnts) > 0:
        # sort the contours according to their size in
        # descending order
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

        # loop over the sorted contours
        for c in cnts:
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # if our approximated contour has four points,
            # then we can assume we have found the paper
            if len(approx) == 4:
                docCnt = approx
                break

    # apply a four point perspective transform to both the
    # original image and grayscale image to obtain a top-down
    # birds eye view of the paper
    paper = four_point_transform(image, docCnt.reshape(4, 2))
    warped = four_point_transform(gray, docCnt.reshape(4, 2))
    #paper = image;
    #warped = gray;

    # apply Otsu's thresholding method to binarize the warped
    # piece of paper
    thresh = cv2.threshold(warped, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

    # find contours in the thresholded image, then initialize
    # the list of contours that correspond to questions
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    questionCnts = []

    for c in cnts:
        # compute the bounding box of the contour, then use the
        # bounding box to derive the aspect ratio
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)

        # in order to label the contour as a question, region
        # should be sufficiently wide, sufficiently tall, and
        # have an aspect ratio approximately equal to 1
        if (w >= circleRadius and h >= circleRadius and ar >= 0.8 and ar <= 1.2):
            questionCnts.append(c)

    # sort the question contours top-to-bottom, then initialize
    # the total number of correct answers
    questionCnts = contours.sort_contours(questionCnts,
                                          method="top-to-bottom")[0]

    correct = 0;

    # loop for each row
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 10)):
        # sort contours from left to right
        cnts = contours.sort_contours(questionCnts[i:i + 10])[0]
        # loop for 5 by once
        for col in range(0, 2):
            marked = 0
            marked_list = []
            for (j, c) in enumerate(cnts[col*5:col*5+5], col*5):
                # create a mask to check if it is marked or not
                mask = np.zeros(thresh.shape, dtype="uint8")
                cv2.drawContours(mask, [c], -1, 255, -1)
                # check
                mask = cv2.bitwise_and(thresh, thresh, mask=mask)
                total = cv2.countNonZero(mask)
                #print(q, j, total)

                # if 1 bypassed a certain value, answer is marked
                if(total > MARKED_COUNT):
                    marked += 1
                    #cv2.drawContours(paper, c, -1, (255, 0, 0), 2)
                    marked_list.append(j);
                #else:
                    #cv2.drawContours(paper, c, -1, (0, 255, 0), 2)
                cv2.imshow("img", paper)
                cv2.waitKey(50);
            print("marked = ", marked)
            # if one is marked, check if it is true or false
            if marked == 1:
                correctanswer = answer[col*10+q]
                print("Correct answer: ", answer[col*10+q])
                print("Marked: ", marked_list[0]-(5*col))
                if marked_list.count(correctanswer+5*col) > 0:
                    print("right")
                    correct += 1
                    cv2.drawContours(paper, cnts[marked_list.pop()], -1, (0, 255, 0), 2)
                else:
                    print("wrong")
                    cv2.drawContours(paper, cnts[marked_list.pop()], -1, (0, 0, 255), 2)
            # 2 or more answer, doesn't give point
            elif marked >= 2:
                for (j, c) in enumerate(cnts[col * 5:col * 5 + 5], col * 5):
                    if marked_list.count(j) > 0:
                        cv2.drawContours(paper, c, -1, (0, 0, 255), 2);
            # no answer as well
            elif marked == 0:
                for (j, c) in enumerate(cnts[col * 5:col * 5 + 5], col * 5):
                    cv2.drawContours(paper, c, -1, (0, 0, 255), 2);

    print("Correct answer: ", correct);
    #paper = cv2.resize(paper, (600, 800));
    cv2.imshow("img", paper);
    cv2.destroyAllWindows()
    cv2.waitKey(0);
    return correct;