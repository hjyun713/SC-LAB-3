
from main_func import *

# first_page = uic.loadUiType("ui_0_new.ui")[0]
# static_page = uic.loadUiType("ui_static_new.ui")[0]
# dynamic_page = uic.loadUiType("ui_dynamic_new.ui")[0]

first_page = uic.loadUiType("./ui/ui_0.ui")[0]
static_page = uic.loadUiType("./ui/ui_static.ui")[0]
dynamic_page = uic.loadUiType("./ui/ui_dynamic.ui")[0]
pt_page = uic.loadUiType("./ui/pt_select.ui")[0]
about_page = uic.loadUiType("./ui/about.ui")[0]

class AboutDialog(QDialog, about_page):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.ok_btn.clicked.connect(self.close)


class Window_1st(QMainWindow, first_page):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.static_btn.clicked.connect(self.static_win)
        self.dynamic_btn.clicked.connect(self.dynamic_win)

        self.about_btn.clicked.connect(self.about_dialog)

    def about_dialog(self):
        dialog = AboutDialog()
        dialog.exec_()


    def static_win(self):
        self.hide()
        select_window.selected_page(0)
        select_window.clearMark()
        select_window.show()

    def dynamic_win(self):
        self.hide()
        select_window.selected_page(1)
        select_window.clearMark()
        select_window.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', 'Exit now?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class CustomGraphicsView(QGraphicsView):
    def __init__(self, parent, *args, **kwargs):
        super(CustomGraphicsView, self).__init__(*args, **kwargs)
        self._parent = parent

        self.mode_flag = 1

        self.box_x = 0
        self.box_y = 0
        self.box_w = 0
        self.box_h = 0

    def wheelEvent(self, event):
        # 마우스 휠 이벤트를 사용하여 확대/축소 기능을 추가
        zoomInFactor = 1.25
        zoomOutFactor = 1 / zoomInFactor

        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
            
        # 현재 스케일 확인
        transform = self.transform()
        curScale = transform.m11()  # m11()은 x 방향의 스케일을 반환합니다.

        # 스케일이 임계치 이상인지 확인
        if (curScale * zoomFactor >= 30.0) and (curScale * zoomFactor <= 400.0):  # 30.0은 임계치, 이 값을 변경하면 임계치를 조정할 수 있습니다.
            self.scale(zoomFactor, zoomFactor)

            # 슬라이더 값 업데이트
            current_value = self._parent.size_slider.value()
            self._parent.size_slider.setValue(int(current_value * zoomFactor))
    
    # def mousePressEvent(self, event):
    #     super().mousePressEvent(event)

    #     if self.mode_flag == 0:
    #         # self.setDragMode(QGraphicsView.NoDrag)  # RubberBand 모드를 종료
    #         self.setDragMode(QGraphicsView.ScrollHandDrag)
    #     else:
    #         # self.setDragMode(QGraphicsView.NoDrag)  # RubberBand 모드를 종료
    #         self.setDragMode(QGraphicsView.RubberBandDrag)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        if self.mode_flag == 0:
            pass
        else:
            # 이동 중인 마우스의 현재 위치를 얻어옵니다.
            rubberband_rect = self.rubberBandRect()
            self.box_x = rubberband_rect.x()
            self.box_y = rubberband_rect.y()
            self.box_w = rubberband_rect.width()
            self.box_h = rubberband_rect.height()
    
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self.mode_flag == 0:
            pass
        else:
            # 화면 좌표를 씬 좌표로 변환합니다.
            self._parent.box_rect = QRect(self.box_x, self.box_y, self.box_w, self.box_h)

            # self._parent.draw_rubberband_box()
            self._parent.get_selected_landmarks()
            self._parent.selected_landmarks_change_color()
            self._parent.draw_box_around_select_landmarks()

class PtSelectWin(QMainWindow, pt_page):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.aftr_page = 0
        self.cls_flag = True

        # 랜드마크 포인트 리스트
        num_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219]
        left_list = [109, 108, 107, 67, 69, 66, 103, 104, 105, 54, 68, 63, 21, 71, 70, 162, 139, 156, 127, 34, 143, 35, 124, 46, 53, 52, 65, 55, 226, 113, 225, 224, 223, 222, 221, 193, 130, 247, 30, 29, 27, 28, 56, 189, 190, 33, 246, 161, 160, 159, 158, 157, 173, 133, 7, 163, 144, 145, 153, 154, 155, 25, 110, 24, 23, 22, 26, 112, 243, 244, 245, 122, 31, 228, 229, 230, 231, 232, 233, 111, 117, 118, 119, 120, 121, 128, 234, 227, 116, 100, 47, 114, 188, 142, 126, 217, 174, 196, 209, 198, 236, 3, 129, 49, 131, 134, 51, 102, 48, 115, 220, 45, 64, 219, 218, 237, 44, 235, 166, 79, 239, 98, 240, 59, 75, 60, 20, 238, 241, 125, 242, 141, 99, 97, 93, 137, 123, 50, 101, 36, 203, 205, 206, 132, 177, 147, 187, 207, 58, 215, 213, 172, 138, 192, 216, 92, 165, 167, 212, 186, 57, 185, 40, 39, 37, 61, 76, 62, 184, 74, 73, 72, 183, 42, 41, 38, 78, 191, 80, 81, 82, 95, 88, 178, 87, 96, 89, 179, 86, 77, 90, 180, 85, 146, 91, 181, 84, 202, 43, 106, 182, 83, 204, 194, 201, 214, 210, 211, 32, 208, 135, 169, 170, 140, 171, 136, 150, 149, 176, 148]
        right_list = [338, 337, 336, 297, 299, 296, 332, 333, 334, 284, 298, 293, 251, 301, 300, 389, 368, 383, 356, 264, 372, 265, 353, 276, 283, 282, 295, 285, 446, 342, 445, 444, 443, 442, 441, 417, 359, 467, 260, 259, 257, 258, 286, 413, 414, 263, 466, 388, 387, 386, 385, 384, 398, 362, 249, 390, 373, 374, 380, 381, 382, 255, 339, 254, 253, 252, 256, 341, 463, 464, 465, 351, 261, 448, 449, 450, 451, 452, 453, 340, 346, 347, 348, 349, 350, 357, 454, 447, 345, 329, 277, 343, 412, 371, 355, 437, 399, 419, 429, 420, 456, 248, 358, 279, 360, 363, 281, 331, 278, 344, 440, 275, 294, 439, 438, 457, 274, 455, 392, 309, 459, 327, 460, 289, 305, 290, 250, 458, 461, 354, 462, 370, 328, 326, 323, 366, 352, 280, 330, 266, 423, 425, 426, 361, 401, 376, 411, 427, 288, 435, 433, 397, 367, 416, 436, 322, 391, 393, 432, 410, 287, 409, 270, 269, 267, 291, 306, 292, 408, 304, 303, 302, 407, 272, 271, 268, 308, 415, 310, 311, 312, 324, 318, 402, 317, 325, 319, 403, 316, 307, 320, 404, 315, 375, 321, 405, 314, 422, 273, 335, 406, 313, 424, 418, 421, 434, 430, 431, 262, 428, 364, 394, 395, 369, 396, 365, 379, 378, 400, 377]

        xpt = [-0.0, -0.0, -0.0, 0.463928, -0.0, -0.0, -0.0, 4.253081, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, -0.0, 0.416106, 7.08796, 2.628639, 3.198363, 3.775151, 4.465819, 2.164289, 3.208229, 2.673803, 3.745193, 4.161018, 5.062006, 2.266659, 4.445859, 7.21453, 5.799793, 2.844939, 0.711452, 0.606033, 1.431615, 1.91491, 1.131043, 1.563548, 2.650112, 0.427049, 0.496396, 5.253307, 1.718698, 1.608635, 1.651267, 4.765501, 0.478306, 3.734964, 4.588603, 6.279331, 1.220941, 2.193489, 3.102642, 6.719682, 1.193824, 0.729766, 2.456206, 2.204823, 4.985894, 1.592294, 2.644548, 2.760292, 3.523964, 5.599763, 3.063932, 5.720968, 6.374393, 0.672728, 1.26256, 1.732553, 1.043625, 2.321234, 2.056846, 2.153084, 0.946874, 1.469132, 1.02434, 0.533422, 0.76972, 0.699606, 0.669687, 0.630947, 0.583218, 1.53717, 1.6156, 1.729053, 1.838624, 2.36825, 7.542244, -0.0, 1.826614, 1.929558, 0.597442, 1.405627, 0.662449, 2.34234, 3.327324, 1.726175, 5.133204, 4.538641, 3.986562, 2.169681, 1.395634, 1.6195, 1.891399, 4.195832, 5.733342, 1.859887, 4.988612, 1.303263, 1.305757, 6.46517, 5.258659, 4.432338, 3.300681, 2.430178, 1.820731, 0.563221, 6.338145, 5.587698, 0.242624, 1.611251, 7.743095, 1.391142, 1.785794, 4.670959, 1.33397, 7.270895, 1.856432, 0.923388, 5.000589, 5.085276, 7.159291, 5.843051, 6.847258, 2.412942, 0.179909, 2.103655, 6.407571, 3.670075, 3.177186, 2.196121, 6.234883, 1.292924, 3.210651, 4.068926, -0.0, -0.0, 2.724032, 2.28846, 1.998311, 6.13004, 2.28846, 2.724032, 3.177186, 3.670075, 4.018389, 7.555811, 4.018389, -0.0, 1.776217, 1.222237, 0.731493, -0.0, 4.135272, 3.311811, 1.313701, 5.940524, 1.998311, 0.901447, -0.0, 2.308977, 6.954154, 1.098819, 1.181124, 1.255818, 1.325085, 1.546388, 1.953754, 2.117802, 2.285339, 2.85016, 5.278538, 0.946709, 1.314173, 1.78, 1.84511, 5.436187, 0.766444, 1.938616, -0.0, 0.516573, -0.0, 1.246815, -0.0, -0.0, 0.997827, 3.288807, 2.311631, 2.68025, 3.832928, 2.96186, 4.386901, 1.217295, 1.542374, 3.878377, 3.084037, 3.747321, 6.094129, 4.588995, 6.583231, 3.49258, 1.255543, 1.126122, 1.443109, 0.923043, 1.755386, 2.632589, 3.388062, 4.075766, 4.62291, 5.171755, 7.297331, 4.706828, 4.071712, 3.269817, 2.527572, 1.970894, 1.579543, 7.664182, 1.397041, 0.884838, 0.767097, 0.460213, 0.748618, 1.236408, 0.387306, 0.319925, 1.639633, 1.255645, 1.031362, 4.253081, 4.53, -0.463928, -4.253081, -0.416106, -7.08796, -2.628639, -3.198363, -3.775151, -4.465819, -2.164289, -3.208229, -2.673803, -3.745193, -4.161018, -5.062006, -2.266659, -4.445859, -7.21453, -5.799793, -2.844939, -0.711452, -0.606033, -1.431615, -1.91491, -1.131043, -1.563548, -2.650112, -0.427049, -0.496396, -5.253307, -1.718698, -1.608635, -1.651267, -4.765501, -0.478306, -3.734964, -4.588603, -6.279331, -1.220941, -2.193489, -3.102642, -6.719682, -1.193824, -0.729766, -2.456206, -2.204823, -4.985894, -1.592294, -2.644548, -2.760292, -3.523964, -5.599763, -3.063932, -5.720968, -6.374393, -0.672728, -1.26256, -1.732553, -1.043625, -2.321234, -2.056846, -2.153084, -0.946874, -1.469132, -1.02434, -0.533422, -0.76972, -0.699606, -0.669687, -0.630947, -0.583218, -1.53717, -1.6156, -1.729053, -1.838624, -2.36825, -7.542244, -1.826614, -1.929558, -0.597442, -1.405627, -0.662449, -2.34234, -3.327324, -1.726175, -5.133204, -4.538641, -3.986562, -2.169681, -1.395634, -1.6195, -1.891399, -4.195832, -5.733342, -1.859887, -4.988612, -1.303263, -1.305757, -6.46517, -5.258659, -4.432338, -3.300681, -2.430178, -1.820731, -0.563221, -6.338145, -5.587698, -0.242624, -1.611251, -7.743095, -1.391142, -1.785794, -4.670959, -1.33397, -7.270895, -1.856432, -0.923388, -5.000589, -5.085276, -7.159291, -5.843051, -6.847258, -2.412942, -0.179909, -2.103655, -6.407571, -3.670075, -3.177186, -2.196121, -6.234883, -1.292924, -3.210651, -4.068926, -2.724032, -2.28846, -1.998311, -6.13004, -2.28846, -2.724032, -3.177186, -3.670075, -4.018389, -7.555811, -4.018389, -1.776217, -1.222237, -0.731493, -4.135272, -3.311811, -1.313701, -5.940524, -1.998311, -0.901447, -2.308977, -6.954154, -1.098819, -1.181124, -1.255818, -1.325085, -1.546388, -1.953754, -2.117802, -2.285339, -2.85016, -5.278538, -0.946709, -1.314173, -1.78, -1.84511, -5.436187, -0.766444, -1.938616, -0.516573, -1.246815, -0.997827, -3.288807, -2.311631, -2.68025, -3.832928, -2.96186, -4.386901, -1.217295, -1.542374, -3.878377, -3.084037, -3.747321, -6.094129, -4.588995, -6.583231, -3.49258, -1.255543, -1.126122, -1.443109, -0.923043, -1.755386, -2.632589, -3.388062, -4.075766, -4.62291, -5.171755, -7.297331, -4.706828, -4.071712, -3.269817, -2.527572, -1.970894, -1.579543, -7.664182, -1.397041, -0.884838, -0.767097, -0.460213, -0.748618, -1.236408, -0.387306, -0.319925, -1.639633, -1.255645, -1.031362, -4.253081, -4.53]
        ypt = [3.406404, 1.126865, 2.089024, -0.955357, 0.46317, -0.365669, -2.473255, -2.577646, -4.019042, -4.885979, -8.261778, 3.706811, 3.918301, 3.994436, 4.5424, 4.745577, 5.019567, 5.365123, 6.149624, 1.501095, 1.466449, -5.434801, -2.035898, -1.985815, -2.039402, -2.42295, -2.189867, -3.223926, -3.205337, -3.165286, -3.059069, -1.934418, 7.425768, -2.663991, -2.263009, -2.349546, 0.720868, 3.329355, 3.924562, 3.500953, 3.803146, 3.973937, 4.082763, 5.003649, 1.094134, 0.475659, -3.881582, -0.974609, 0.942516, 0.610868, 0.701554, -0.295766, -4.50823, -4.302037, -6.615427, -4.142165, -3.100317, 4.352984, 4.788645, 1.306795, 1.593712, 4.342621, 4.304508, -4.802461, 1.257709, -4.524654, -5.100971, -8.005976, -5.71547, -6.566144, -4.254584, -4.78559, 3.688016, 3.787691, 3.952767, 1.464973, 4.329069, 4.477671, 4.276322, 1.035249, 4.036351, 3.989851, 3.993222, 6.095394, 5.29185, 4.94977, 4.695101, 4.517982, 4.423206, 4.475942, 4.61868, 4.828746, 3.106237, 1.049282, 1.724003, 4.399531, 4.411831, 2.013686, 1.714196, 1.819321, -0.572222, -0.104863, 0.919165, -7.485602, -6.319907, -5.109487, 5.440433, -5.011963, -6.599217, -8.236377, -2.235205, -1.411738, -2.355757, -3.074654, -1.416453, 0.672779, -0.937119, -0.945811, -0.722096, -0.861641, -1.131492, -1.467954, -2.307693, 0.529279, -3.208071, 1.462857, -0.339326, -2.364999, -1.851048, 0.978284, -2.664461, 0.283761, 2.890917, -2.585245, -0.073076, 6.135128, 7.17859, 0.81182, 5.248023, -3.662916, 8.258853, 1.689864, 0.163946, -2.236021, -2.360153, -2.294265, 4.598322, 1.94443, 9.29592, 8.533278, 7.993109, -6.54539, 9.403378, -2.315802, -2.398891, -2.496547, -3.399261, -2.886504, -2.96181, -2.964136, -2.927714, -2.857357, -4.106811, -2.483695, 2.521945, 2.683946, 1.182444, 2.536683, -3.271027, 6.996638, 7.660815, 8.639995, 6.223629, -2.743838, -1.236992, 8.765243, 8.974196, 2.439843, 4.458788, 4.579996, 4.787901, 5.106507, 5.819392, 4.183892, 4.137093, 4.051196, 3.66572, 2.238942, -1.907628, -3.104912, -2.86, 4.09888, 4.030482, -3.182131, 6.61441, -1.059413, -1.583572, -1.728369, -0.230297, 7.942194, 6.991499, 6.930921, 5.382514, 1.566237, 6.111567, 1.537326, 2.274215, 2.683286, 7.834465, 0.136843, 6.041764, 6.809842, 4.503545, 3.205991, 4.728726, 3.941269, 3.19582, -0.802341, 0.933602, 1.142774, 0.529042, -3.529117, -3.713828, -3.721976, -3.675413, -3.474691, -2.535753, -0.763172, -1.651, -1.476821, -1.470659, -1.617311, -1.858505, -2.097941, -0.673132, 1.340139, -0.65874, 0.968035, 1.334106, 1.067994, 1.585568, 1.40999, 1.607931, -2.556298, -2.467144, -2.382663, -2.772296, -2.91, -0.955357, -2.577646, 1.466449, -5.434801, -2.035898, -1.985815, -2.039402, -2.42295, -2.189867, -3.223926, -3.205337, -3.165286, -3.059069, -1.934418, 7.425768, -2.663991, -2.263009, -2.349546, 0.720868, 3.329355, 3.924562, 3.500953, 3.803146, 3.973937, 4.082763, 5.003649, 1.094134, 0.475659, -3.881582, -0.974609, 0.942516, 0.610868, 0.701554, -0.295766, -4.50823, -4.302037, -6.615427, -4.142165, -3.100317, 4.352984, 4.788645, 1.306795, 1.593712, 4.342621, 4.304508, -4.802461, 1.257709, -4.524654, -5.100971, -8.005976, -5.71547, -6.566144, -4.254584, -4.78559, 3.688016, 3.787691, 3.952767, 1.464973, 4.329069, 4.477671, 4.276322, 1.035249, 4.036351, 3.989851, 3.993222, 6.095394, 5.29185, 4.94977, 4.695101, 4.517982, 4.423206, 4.475942, 4.61868, 4.828746, 3.106237, 1.049282, 4.399531, 4.411831, 2.013686, 1.714196, 1.819321, -0.572222, -0.104863, 0.919165, -7.485602, -6.319907, -5.109487, 5.440433, -5.011963, -6.599217, -8.236377, -2.235205, -1.411738, -2.355757, -3.074654, -1.416453, 0.672779, -0.937119, -0.945811, -0.722096, -0.861641, -1.131492, -1.467954, -2.307693, 0.529279, -3.208071, 1.462857, -0.339326, -2.364999, -1.851048, 0.978284, -2.664461, 0.283761, 2.890917, -2.585245, -0.073076, 6.135128, 7.17859, 0.81182, 5.248023, -3.662916, 8.258853, 1.689864, 0.163946, -2.236021, -2.360153, -2.294265, 4.598322, 1.94443, 9.29592, 8.533278, 7.993109, -2.315802, -2.398891, -2.496547, -3.399261, -2.886504, -2.96181, -2.964136, -2.927714, -2.857357, -4.106811, -2.483695, 2.683946, 1.182444, 2.536683, 6.996638, 7.660815, 8.639995, 6.223629, -2.743838, -1.236992, 8.974196, 2.439843, 4.458788, 4.579996, 4.787901, 5.106507, 5.819392, 4.183892, 4.137093, 4.051196, 3.66572, 2.238942, -1.907628, -3.104912, -2.86, 4.09888, 4.030482, -3.182131, 6.61441, -1.583572, -0.230297, 6.930921, 5.382514, 1.566237, 6.111567, 1.537326, 2.274215, 2.683286, 7.834465, 0.136843, 6.041764, 6.809842, 4.503545, 3.205991, 4.728726, 3.941269, 3.19582, -0.802341, 0.933602, 1.142774, 0.529042, -3.529117, -3.713828, -3.721976, -3.675413, -3.474691, -2.535753, -0.763172, -1.651, -1.476821, -1.470659, -1.617311, -1.858505, -2.097941, -0.673132, 1.340139, -0.65874, 0.968035, 1.334106, 1.067994, 1.585568, 1.40999, 1.607931, -2.556298, -2.467144, -2.382663, -2.772296, -2.91]
        # zpt = [5.979507, 7.475604, 6.058267, 6.633583, 7.58658, 7.24287, 5.788627, 3.279702, 5.284764, 5.385258, 4.481535, 5.864924, 5.56943, 5.219482, 5.404754, 5.529457, 5.601448, 5.535441, 5.071372, 7.112196, 6.447657, 0.09962, 3.848121, 3.796952, 3.646194, 3.155168, 3.851822, 4.115822, 4.092203, 3.972409, 3.719554, 2.776093, 4.389812, 3.173422, 0.07315, 2.204059, 4.43313, 5.877044, 5.444923, 5.496189, 5.02893, 5.189648, 4.842263, 4.188483, 7.360529, 7.440358, 3.363159, 4.558359, 5.814193, 5.581319, 3.534632, 7.101013, 4.550454, 4.048484, 1.42585, 5.106035, 4.000575, 4.095905, -1.745401, 5.737747, 5.833208, 4.283884, 4.162499, 3.751977, 5.456949, 4.921559, 5.01599, 3.729163, 2.724259, 4.529981, 2.830852, 1.591691, 5.737804, 5.417779, 5.000579, 5.662455, 4.258156, 4.520883, 4.038093, 6.512274, 4.604908, 4.926693, 5.138202, 4.985883, 5.448304, 5.509612, 5.449371, 5.339869, 4.74547, 4.813632, 4.854463, 4.823737, 4.868096, -2.431321, 6.60139, 4.399021, 4.497052, 5.866456, 5.241087, 5.863759, 4.294303, 4.11386, 5.273355, 2.660442, 3.683424, 4.466315, 4.455874, 5.316032, 4.921106, 4.274997, 3.375099, 2.431726, 3.843181, 3.083858, 4.831091, 6.415959, 1.689873, 2.974312, 3.522615, 3.872784, 4.039035, 4.224124, 5.566789, 1.881175, 2.687839, 7.071491, 4.895421, -2.005167, 4.448999, 4.85047, 3.084075, 6.097047, -2.252455, 3.757904, 6.671944, 1.892523, 0.714711, -0.072044, 0.924091, 0.724695, 4.119213, 6.573301, 4.566119, 1.560843, 3.63523, 3.775704, 4.479786, 1.663542, 4.094063, 2.802001, 1.925119, 5.027311, 4.264492, 3.777151, 3.697603, 3.689148, 2.038516, 3.775031, 3.871767, 3.876973, 3.724325, 3.482983, -0.991917, 3.440898, 5.932265, 5.213116, 5.952465, 5.815343, 5.236015, 2.67197, 3.382963, 4.702456, -0.631468, 3.74403, 5.754256, 4.891441, 3.60907, -0.131163, 5.120727, 5.189564, 5.237051, 5.20501, 4.757893, 4.431713, 4.555096, 4.582438, 4.484994, 2.861224, 5.196779, 4.231404, 3.881555, 4.247264, 2.109852, 4.861453, 4.521085, 6.774605, 6.148363, 6.31675, 5.681036, 5.181173, 5.153478, 4.979576, 3.795752, 4.590085, 4.096152, 4.137731, 4.440943, 3.643886, 4.969286, 5.201008, 3.311079, 3.814195, 3.726453, 1.473482, 2.983221, 0.070268, 4.130198, 5.307551, 6.538785, 5.905127, 7.003423, 4.327696, 4.364629, 4.309028, 4.076063, 3.646321, 2.670867, -0.048769, 3.109532, 3.476944, 3.731945, 3.865444, 3.961782, 4.084996, -2.435867, 5.630378, 6.233232, 7.077932, 6.787447, 6.798303, 5.48049, 6.957705, 6.508676, 3.863736, 4.2038, 4.615849, 3.315305, 3.339685, 6.633583, 3.279702, 6.447657, 0.09962, 3.848121, 3.796952, 3.646194, 3.155168, 3.851822, 4.115822, 4.092203, 3.972409, 3.719554, 2.776093, 4.389812, 3.173422, 0.07315, 2.204059, 4.43313, 5.877044, 5.444923, 5.496189, 5.02893, 5.189648, 4.842263, 4.188483, 7.360529, 7.440358, 3.363159, 4.558359, 5.814193, 5.581319, 3.534632, 7.101013, 4.550454, 4.048484, 1.42585, 5.106035, 4.000575, 4.095905, -1.745401, 5.737747, 5.833208, 4.283884, 4.162499, 3.751977, 5.456949, 4.921559, 5.01599, 3.729163, 2.724259, 4.529981, 2.830852, 1.591691, 5.737804, 5.417779, 5.000579, 5.662455, 4.258156, 4.520883, 4.038093, 6.512274, 4.604908, 4.926693, 5.138202, 4.985883, 5.448304, 5.509612, 5.449371, 5.339869, 4.74547, 4.813632, 4.854463, 4.823737, 4.868096, -2.431321, 4.399021, 4.497052, 5.866456, 5.241087, 5.863759, 4.294303, 4.11386, 5.273355, 2.660442, 3.683424, 4.466315, 4.455874, 5.316032, 4.921106, 4.274997, 3.375099, 2.431726, 3.843181, 3.083858, 4.831091, 6.415959, 1.689873, 2.974312, 3.522615, 3.872784, 4.039035, 4.224124, 5.566789, 1.881175, 2.687839, 7.071491, 4.895421, -2.005167, 4.448999, 4.85047, 3.084075, 6.097047, -2.252455, 3.757904, 6.671944, 1.892523, 0.714711, -0.072044, 0.924091, 0.724695, 4.119213, 6.573301, 4.566119, 1.560843, 3.63523, 3.775704, 4.479786, 1.663542, 4.094063, 2.802001, 1.925119, 3.777151, 3.697603, 3.689148, 2.038516, 3.775031, 3.871767, 3.876973, 3.724325, 3.482983, -0.991917, 3.440898, 5.213116, 5.952465, 5.815343, 2.67197, 3.382963, 4.702456, -0.631468, 3.74403, 5.754256, 3.60907, -0.131163, 5.120727, 5.189564, 5.237051, 5.20501, 4.757893, 4.431713, 4.555096, 4.582438, 4.484994, 2.861224, 5.196779, 4.231404, 3.881555, 4.247264, 2.109852, 4.861453, 4.521085, 6.148363, 5.681036, 4.979576, 3.795752, 4.590085, 4.096152, 4.137731, 4.440943, 3.643886, 4.969286, 5.201008, 3.311079, 3.814195, 3.726453, 1.473482, 2.983221, 0.070268, 4.130198, 5.307551, 6.538785, 5.905127, 7.003423, 4.327696, 4.364629, 4.309028, 4.076063, 3.646321, 2.670867, -0.048769, 3.109532, 3.476944, 3.731945, 3.865444, 3.961782, 4.084996, -2.435867, 5.630378, 6.233232, 7.077932, 6.787447, 6.798303, 5.48049, 6.957705, 6.508676, 3.863736, 4.2038, 4.615849, 3.315305, 3.339685]

        mid_list = [10, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 11, 12, 13, 14, 15, 16, 17, 18, 200, 199, 175, 152]

        self.x_landmarks = []
        self.y_landmarks = []
        self.list_pt = []
        for idx, data in enumerate(left_list):
            self.x_landmarks.append(xpt[data] * -1)
            self.y_landmarks.append(ypt[data])
            self.list_pt.append(num_list[idx])

        for idx, data in enumerate(mid_list):
            self.x_landmarks.append(xpt[data] * -1)
            self.y_landmarks.append(ypt[data])
            self.list_pt.append(222)
        
        # 랜드마크 선택 관련
        self.selected_landmarks = []
        self.box_rect = QRect(0, 0, 0, 0)
        self.setbox_flag = False

        # 라디오 버튼
        self.drag_mode.toggled.connect(self.onRadioButtonToggled)
        self.select_mode.toggled.connect(self.onRadioButtonToggled)
        self.select_mode.setChecked(True)

        self.add_chk.toggled.connect(self.onRadioButtonToggled)
        self.del_chk.toggled.connect(self.onRadioButtonToggled)
        self.add_chk.setChecked(True)

        self.add_toggle = True
        self.del_toggle = False

        # next, clear 버튼
        self.next_btn.clicked.connect(self.nextStep)
        self.clear_btn.clicked.connect(self.clearMark)

        # 슬라이더
        self.c_loc = 30
        self.size_slider.sliderMoved.connect(self.set_position)
        self.size_slider.setRange(30, 300)
        self.size_slider.setValue(30)

        # landmark 설정
        self.setmarkcolor = Qt.blue
        self.mark_color.addItems(['Red', 'Blue', 'Green'])
        self.mark_color.setCurrentText('Blue')
        self.mark_color.activated.connect(self.mark_color_handle)
        
        self.setselectcolor = Qt.red
        self.select_color.addItems(['Red', 'Blue', 'Green'])
        self.select_color.setCurrentText('Red')
        self.select_color.activated.connect(self.select_color_handle)

        # box 설정 변수
        self.boxsize = 0.05
        self.box_size.setMinimum(0.01)
        self.box_size.setMaximum(0.5)
        self.box_size.setValue(0.05)
        self.box_size.setSingleStep(0.01)
        self.box_size.valueChanged.connect(self.box_size_handle)

        self.setboxcolor = Qt.green
        self.box_color.addItems(['Red', 'Blue', 'Green'])
        self.box_color.setCurrentText('Green')
        self.box_color.activated.connect(self.box_color_handle)

        # 그래프 설정
        self.graphicsView.deleteLater()  # 기존 graphicsView를 삭제
        self.graphicsView = CustomGraphicsView(self, self.splitter)  # 새로운 graphicsView 생성
        # self.splitter_3.addWidget(self.graphicsView, 0, 0, 1, 1)  # 새로운 graphicsView를 레이아웃에 추가

        self.graphicsView.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        # 초기 확대/축소 값 설정
        initial_scale_factor = 30.0  # 1.0은 원래 크기, 2.0은 2배 확대, 0.5는 2배 축소 등
        self.graphicsView.setTransform(self.graphicsView.transform().scale(initial_scale_factor, initial_scale_factor))

        self.graphicsView.setRenderHint(QPainter.Antialiasing)
        self.graphicsView.setRenderHint(QPainter.SmoothPixmapTransform)

        self.graphicsView.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, False)
        self.graphicsView.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)

        self.graphicsView.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.graphicsView.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        self.draw_Landmark_graph()
        self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)

    def selected_page(self, aftr_page = 0):
        self.aftr_page = aftr_page

    def draw_Landmark_graph(self):
        # 랜드마크 포인트 출력
        for idx, (x, y) in enumerate(zip(self.x_landmarks, self.y_landmarks)):
            point = QGraphicsEllipseItem(QRectF(x, y, 0.1, 0.1))  # QGraphicsRectItem 대신 QGraphicsEllipseItem 사용
            point.setBrush(QBrush(self.setmarkcolor))
            point.setPen(QPen(Qt.NoPen))
            # point.setData(0, idx)
            point.setData(0, self.list_pt[idx])
            self.scene.addItem(point)

    def draw_rubberband_box(self):
        # # 이전에 그려진 박스를 삭제합니다.
        # if hasattr(self, "rubberband_box"):
        #     self.setbox_flag = False
        #     self.scene.removeItem(self.rubberband_box)
        
        scene_rect = self.graphicsView.mapToScene(self.box_rect).boundingRect()

        # RubberBand 박스를 그립니다.
        self.rubberband_box = QGraphicsRectItem(scene_rect)
        self.rubberband_box.setBrush(Qt.transparent)
        self.rubberband_box.setPen(QPen(self.setboxcolor, self.boxsize))
        self.scene.addItem(self.rubberband_box)

        self.setbox_flag = True
    
    def subList(self, A, B):
        sub_result = [x for x in A if x not in B]
        return sub_result
    
    def clearMark(self):

        all_landmarks = [item for item in self.scene.items() if isinstance(item, QGraphicsEllipseItem)]

        for item in all_landmarks:
            item.setBrush(QBrush(self.setmarkcolor))
        
        # 이전에 그려진 박스를 삭제합니다.
        if hasattr(self, "rubberband_box"):
            self.setbox_flag = False
            self.scene.removeItem(self.rubberband_box)
        
        self.selected_landmarks = []
        self.log_something(self.selected_landmarks)


    # 드래그 앤 드롭된 RubberBand 안의 랜드마크 가져오기
    def get_selected_landmarks(self):
        try:

            all_landmarks = [item for item in self.scene.items() if isinstance(item, QGraphicsEllipseItem)]
            # 선택한 영역 내에 있는 랜드마크 가져오기
            selected_items = self.graphicsView.items(self.box_rect, mode=Qt.IntersectsItemShape)

            # self.selected_landmarks.clear()  # 이전에 선택한 랜드마크를 초기화합니다.

            for item in all_landmarks:
                if item in selected_items:
                    index = item.data(0)
                    if index == 222:
                        pass
                    else:
                        if self.add_toggle:
                            # 선택된 랜드마크를 리스트에 추가                    
                            self.selected_landmarks.append(index)
                        elif self.del_toggle:
                            # 선택된 랜드마크를 리스트에서 제거
                            if index in self.selected_landmarks:
                                self.selected_landmarks.remove(index)
                            else:
                                pass
                        else:
                            print('chk select mode')
                else:
                    pass
            
            self.selected_landmarks = list(set(self.selected_landmarks))
            self.selected_landmarks.sort()
            self.log_something(self.selected_landmarks)

        except Exception as e:
            print(e)
            traceback.format_exc()
    
    def selected_landmarks_change_color(self):
        try:

            all_landmarks = [item for item in self.scene.items() if isinstance(item, QGraphicsEllipseItem)]
            
            # draw
            for item in all_landmarks:
                index = item.data(0)

                if index in self.selected_landmarks:
                    item.setBrush(QBrush(self.setselectcolor))
                else:
                    item.setBrush(QBrush(self.setmarkcolor))

        except Exception as e:
            print(e)
            traceback.format_exc()
        
    
    def draw_box_around_select_landmarks(self):
        try:
            # 이전에 그려진 박스를 삭제합니다.
            if hasattr(self, "rubberband_box"):
                self.setbox_flag = False
                self.scene.removeItem(self.rubberband_box)

            # 붉은색 랜드마크만 가져옵니다.
            red_landmarks = [item for item in self.scene.items() if isinstance(item, QGraphicsEllipseItem) and item.brush().color() == self.setselectcolor]

            if len(red_landmarks) > 1:
                # 붉은색 랜드마크의 영역을 계산합니다.
                min_x_values = [self.graphicsView.mapFromScene(item.boundingRect().topLeft()).x() for item in red_landmarks]
                min_y_values = [self.graphicsView.mapFromScene(item.boundingRect().topLeft()).y() for item in red_landmarks]
                
                max_x_values = [self.graphicsView.mapFromScene(item.boundingRect().bottomRight()).x() for item in red_landmarks]
                max_y_values = [self.graphicsView.mapFromScene(item.boundingRect().bottomRight()).y() for item in red_landmarks]

                min_x = min(min_x_values)
                min_y = min(min_y_values)
                max_x = max(max_x_values)
                max_y = max(max_y_values)

                # 박스 좌표
                self.box_rect = QRect(min_x, min_y, max_x - min_x, max_y - min_y)

                # 박스 그리기
                self.draw_rubberband_box()
        
        except Exception as e:
            print(e)

    
    def onRadioButtonToggled(self):
        radioButton = self.sender()
        chk_txt = radioButton.text()

        if radioButton.isChecked():
            if chk_txt == 'Drag':
                self.graphicsView.mode_flag = 0
                self.graphicsView.setDragMode(QGraphicsView.ScrollHandDrag)
            elif chk_txt == 'Select':
                self.graphicsView.mode_flag = 1
                self.graphicsView.setDragMode(QGraphicsView.RubberBandDrag)
            elif chk_txt == 'Add':
                self.add_toggle = True
                self.del_toggle = False
            elif chk_txt == 'Delete':
                self.add_toggle = False
                self.del_toggle = True
            else:
                print('except')
                
    
    def set_position(self):
        try:
            self.c_loc = int(self.size_slider.value())
            initial_scale_factor = float(self.c_loc)
            self.graphicsView.resetTransform()
            self.graphicsView.scale(initial_scale_factor, initial_scale_factor)


        except Exception as e:
            print(e)
    
    def mark_color_handle(self):
        selected_item = self.mark_color.currentText()

        if selected_item == 'Red':
            self.setmarkcolor = Qt.red
        elif selected_item == 'Blue':
            self.setmarkcolor = Qt.blue
        elif selected_item == 'Green':
            self.setmarkcolor = Qt.green
        else:
            print('mark color err')
        
        self.selected_landmarks_change_color()
    
    def select_color_handle(self):
        selected_item = self.select_color.currentText()

        if selected_item == 'Red':
            self.setselectcolor = Qt.red
        elif selected_item == 'Blue':
            self.setselectcolor = Qt.blue
        elif selected_item == 'Green':
            self.setselectcolor = Qt.green
        else:
            print('select color err')

        self.selected_landmarks_change_color()

    def box_color_handle(self):
        selected_item = self.box_color.currentText()

        if selected_item == 'Red':
            self.setboxcolor = Qt.red
        elif selected_item == 'Blue':
            self.setboxcolor = Qt.blue
        elif selected_item == 'Green':
            self.setboxcolor = Qt.green
        else:
            print('box color err')

        if hasattr(self, "rubberband_box"):
            self.rubberband_box.setPen(QPen(self.setboxcolor, self.boxsize))
    
    def box_size_handle(self, value):
        self.boxsize = value

        if hasattr(self, "rubberband_box"):
            self.rubberband_box.setPen(QPen(self.setboxcolor, self.boxsize))
    
    def log_something(self, log_list):
        self.log_edit.clear()
        # plainTextEdit에 로그 출력
        self.log_edit.appendPlainText('Select Landmark List:')

        for idx, data in enumerate(log_list):
            if idx % 5 == 0:
                self.log_edit.appendPlainText('\n')

            self.log_edit.insertPlainText(f'{str(data)}')

            if idx == (len(log_list) - 1):
                pass
            else:
                self.log_edit.insertPlainText(f', ')
    
    def nextStep(self):
        self.cls_flag = False

        if len(self.selected_landmarks) == 0:
            QMessageBox.about(self, 'Warning', 'Please Select Landmarks.')
            return

        if self.aftr_page == 0:
            static_window.__init__()
            static_window.selected_landmark(self.selected_landmarks)
            static_window.show()
        elif self.aftr_page == 1:
            dynamic_window.__init__()
            dynamic_window.selected_landmark(self.selected_landmarks)
            dynamic_window.show()
        else:
            print('pass')
        
        self.close()
    
    def closeEvent(self, event):

        if self.cls_flag:
            # 홈으로 이동
            main_window.show()

        self.close()


class Window_Static(QMainWindow, static_page):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.worker = StaticAnalysis()
        self.all_num_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219]

        self.comboBox.addItems(['1', '2', '3'])
        self.comboBox.activated.connect(self.handle_combo_box)

        self.img_load_btn_1.clicked.connect(self.upload_image_1)
        self.img_view_btn_1.clicked.connect(self.view_image_1)
        self.img_load_btn_2.clicked.connect(self.upload_image_2)
        self.img_view_btn_2.clicked.connect(self.view_image_2)
        self.img_load_btn_3.clicked.connect(self.upload_image_3)
        self.img_view_btn_3.clicked.connect(self.view_image_3)

        self.analysis_s_btn.clicked.connect(self.start_analysis)
        self.analysis_s_btn.setEnabled(False)

        self.img_load_btn_1.setEnabled(False)
        self.img_view_btn_1.setEnabled(False)
        self.img_load_btn_2.setEnabled(False)
        self.img_view_btn_2.setEnabled(False)
        self.img_load_btn_3.setEnabled(False)
        self.img_view_btn_3.setEnabled(False)

        # # 저장
        # self.Save_btn.clicked.connect(self.saveFunc)

        self.load_selected = False
        self.item_cnt = 0
        self.img_view_flag = False
        self.current_img_num = 0

        # landmark 설정
        self.p_size = 1
        self.spinBox.setMinimum(1)
        self.spinBox.setValue(1)
        self.spinBox.valueChanged.connect(self.p_spin_handle)

        self.p_color = (255, 0, 0)
        self.cb_color.addItems(['Red', 'Blue', 'Green'])
        self.cb_color.setCurrentText('Blue')
        self.cb_color.activated.connect(self.p_cb_handle)

        # iris 설정
        self.iris_size = 2
        self.spinBox_i.setMinimum(1)
        self.spinBox_i.setValue(2)
        self.spinBox_i.valueChanged.connect(self.i_spin_handle)

        self.iris_color = (0, 0, 255)
        self.cb_color_i.addItems(['Red', 'Blue', 'Green'])
        self.cb_color_i.setCurrentText('Red')
        self.cb_color_i.activated.connect(self.i_cb_handle)

        # line 설정
        self.line_size = 5
        self.spinBox_m.setMinimum(1)
        self.spinBox_m.setValue(5)
        self.spinBox_m.valueChanged.connect(self.ml_spin_handle)

        self.line_color = (0, 255, 0)
        self.cb_color_m.addItems(['Red', 'Blue', 'Green'])
        self.cb_color_m.setCurrentText('Green')
        self.cb_color_m.activated.connect(self.ml_cb_handle)

    def draw_pixmap(self, image, label):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        cimage = QtGui.QImage(image.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        scaled_pixmap = QtGui.QPixmap.fromImage(cimage).scaled(label.size(), QtCore.Qt.KeepAspectRatio)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(QtCore.Qt.AlignCenter)

    def draw_Mark(self):
        try:
            if self.current_img_num == 1:
                img = self.img_1.copy()
                pt_list = self.lp_ori_1
            elif self.current_img_num == 2:
                img = self.img_2.copy()
                pt_list = self.lp_ori_2
            elif self.current_img_num == 3:
                img = self.img_3.copy()
                pt_list = self.lp_ori_3
            else:
                return

            draw_img = draw_landmarks_static(img, pt_list, self.p_color, self.p_size, self.iris_color, self.iris_size, self.line_color, self.line_size)
            self.draw_pixmap(draw_img, self.img_print)

        except Exception as e:
            print(e)
    
    def selected_landmark(self, selected_landmarks):
        self.select_num_list = selected_landmarks
        # self.log_something(f'Select Landmark List : {len(self.select_num_list)}\n{self.select_num_list}\n')
        self.log_something(f'Select Landmark List : {len(self.select_num_list)}')

    def p_cb_handle(self, value):

        selected_item = self.cb_color.currentText()
        
        color_red = (0, 0, 255)
        color_blue = (255, 0, 0)
        color_green = (0, 255, 0)

        if selected_item == 'Red':
            self.p_color = color_red
        elif selected_item == 'Blue':
            self.p_color = color_blue
        elif selected_item == 'Green':
            self.p_color = color_green
        else:
            self.log_something("color err")
        
        if not self.img_view_flag:
            return
        
        self.draw_Mark()

    def p_spin_handle(self, value):

        self.p_size = value

        if not self.img_view_flag:
            return
        
        self.draw_Mark()

    def i_cb_handle(self, value):

        selected_item = self.cb_color_i.currentText()
        
        color_red = (0, 0, 255)
        color_blue = (255, 0, 0)
        color_green = (0, 255, 0)

        if selected_item == 'Red':
            self.iris_color = color_red
        elif selected_item == 'Blue':
            self.iris_color = color_blue
        elif selected_item == 'Green':
            self.iris_color = color_green
        else:
            self.log_something("color err")

        if not self.img_view_flag:
            return
        self.draw_Mark()

    def i_spin_handle(self, value):

        self.iris_size = value

        if not self.img_view_flag:
            return
        
        self.draw_Mark()

    def ml_cb_handle(self, value):

        selected_item = self.cb_color_m.currentText()
        
        color_blue = (0, 0, 255)
        color_red = (255, 0, 0)
        color_green = (0, 255, 0)

        if selected_item == 'Red':
            self.line_color = color_red
        elif selected_item == 'Blue':
            self.line_color = color_blue
        elif selected_item == 'Green':
            self.line_color = color_green
        else:
            self.log_something("color err")
        
        if not self.img_view_flag:
            return
        self.draw_Mark()

    def ml_spin_handle(self, value):

        self.line_size = value

        if not self.img_view_flag:
            return
        
        self.draw_Mark()


    def handle_combo_box(self):
        selected_item = self.comboBox.currentText()
        self.analysis_s_btn.setEnabled(False)
        self.img_view_flag = False

        if selected_item == '1':
            self.img_load_btn_1.setEnabled(True)
            self.img_view_btn_1.setEnabled(True)
            self.img_load_btn_2.setEnabled(False)
            self.img_view_btn_2.setEnabled(False)
            self.img_load_btn_3.setEnabled(False)
            self.img_view_btn_3.setEnabled(False)
            self.load_selected = True
            self.item_cnt = 1

        elif selected_item == '2':
            self.img_load_btn_1.setEnabled(True)
            self.img_view_btn_1.setEnabled(True)
            self.img_load_btn_2.setEnabled(True)
            self.img_view_btn_2.setEnabled(True)
            self.img_load_btn_3.setEnabled(False)
            self.img_view_btn_3.setEnabled(False)
            self.load_selected = True
            self.item_cnt = 2

        elif selected_item == '3':
            self.img_load_btn_1.setEnabled(True)
            self.img_view_btn_1.setEnabled(True)
            self.img_load_btn_2.setEnabled(True)
            self.img_view_btn_2.setEnabled(True)
            self.img_load_btn_3.setEnabled(True)
            self.img_view_btn_3.setEnabled(True)
            self.load_selected = True
            self.item_cnt = 3

        else:
            self.item_cnt = 0
            self.load_selected = False
            self.log_something('Select the number of images')
            
    def upload_image_1(self):
        try: 

            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
            if file_path:
                self.img_1, self.lp_ori_1, self.lp_re_1 = self.worker.imgAnalysis(file_path)

                if self.item_cnt == 1:
                    self.analysis_s_btn.setEnabled(True)
                
                link_list = file_path.split('/')
                fname = link_list[len(link_list) - 1]

                self.log_something(f'#1 {fname} loaded')
        except Exception as e:
            print(e)
            self.log_something('#1 Load Fail')
    
    def view_image_1(self):
        try: 
            self.current_img_num = 1
            self.current_frame = self.img_1.copy()
            self.img_view_flag = True

            draw_img = draw_landmarks_static(self.img_1, self.lp_ori_1, self.p_color, self.p_size, self.iris_color, self.iris_size, self.line_color, self.line_size)
            self.draw_pixmap(draw_img, self.img_print)
    
        except:
            self.log_something('#1 View Fail')

    def upload_image_2(self):
        try: 
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
            if file_path:
                self.img_2, self.lp_ori_2, self.lp_re_2 = self.worker.imgAnalysis(file_path)

                if self.item_cnt == 2:
                    self.analysis_s_btn.setEnabled(True)

                link_list = file_path.split('/')
                fname = link_list[len(link_list) - 1]

                self.log_something(f'#2 {fname} loaded')
        except:
            self.log_something('#2 Load Fail')
    
    def view_image_2(self):
        try: 
            self.current_img_num = 2
            self.current_frame = self.img_2.copy()
            self.img_view_flag = True

            draw_img = draw_landmarks_static(self.img_2, self.lp_ori_2, self.p_color, self.p_size, self.iris_color, self.iris_size, self.line_color, self.line_size)
            self.draw_pixmap(draw_img, self.img_print)

        except:
            self.log_something('#2 View Fail')

    def upload_image_3(self):
        try: 
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg)")
            if file_path:
                self.img_3, self.lp_ori_3, self.lp_re_3 = self.worker.imgAnalysis(file_path)

                if self.item_cnt == 3:
                    self.analysis_s_btn.setEnabled(True)

                link_list = file_path.split('/')
                fname = link_list[len(link_list) - 1]

                self.log_something(f'#3 {fname} loaded')
        except:
            self.log_something('#3 Load Fail')
    
    def view_image_3(self):
        try: 
            self.current_img_num = 3
            self.current_frame = self.img_3.copy()
            self.img_view_flag = True

            draw_img = draw_landmarks_static(self.img_3, self.lp_ori_3, self.p_color, self.p_size, self.iris_color, self.iris_size, self.line_color, self.line_size)
            self.draw_pixmap(draw_img, self.img_print)

        except:
            self.log_something('#3 View Fail')
 

    def start_analysis(self):

        # self.log_something('분석 시작.. 잠시만 기다려주세요.')
        now = datetime.now() # 현재 시간을 가져옵니다.
        current_date = now.strftime("%B %d, %Y")
        current_time = now.strftime("%H:%M") # 시간을 hh:mm 형식으로 포맷합니다.
        self.log_something(f"\nHere is the result of the analysis at {current_time} on {current_date}. This shows the distance symmetry score (D.S.S) and angle symmetry score (A.S.S).")

        self.log_something('\n')
        self.log_something('Result of all landmarks')
        self.analysis_func(self.all_num_list)
        
        self.log_something('Result of selected landmarks')
        self.analysis_func(self.select_num_list)
        # self.log_something('-------------------------------------------------------------------------------------------')


    def analysis_func(self, calc_pt_list):

        try:
            selected_item = self.comboBox.currentText()
            if selected_item == '1':
                # 대칭성 연산
                self.lp_re_1 = np.array(self.lp_re_1)
                dist_symm_1, angle_symm_1 = single_symmetry(self.lp_re_1, calc_pt_list)
                self.log_something('#1')
                self.log_something(' -    D.S.S:  %.2f' % dist_symm_1)
                self.log_something(' -    A.S.S:  %.2f' % angle_symm_1)

            elif selected_item == '2':
                # 대칭성 연산
                self.lp_re_1 = np.array(self.lp_re_1)
                self.lp_re_2 = np.array(self.lp_re_2)
                dist_symm_1, angle_symm_1 = single_symmetry(self.lp_re_1, calc_pt_list)
                dist_symm_2, angle_symm_2 = single_symmetry(self.lp_re_2, calc_pt_list)

                self.log_something('#1')
                self.log_something(' -    D.S.S:  %.2f' % dist_symm_1)
                self.log_something(' -    A.S.S:  %.2f' % angle_symm_1)
                self.log_something('#2')
                self.log_something(' -    D.S.S:  %.2f' % dist_symm_2)
                self.log_something(' -    A.S.S:  %.2f' % angle_symm_2)

            elif selected_item == '3':
                # 대칭성 연산
                self.lp_re_1 = np.array(self.lp_re_1)
                self.lp_re_2 = np.array(self.lp_re_2)
                self.lp_re_3 = np.array(self.lp_re_3)
                dist_symm_1, angle_symm_1 = single_symmetry(self.lp_re_1, calc_pt_list)
                dist_symm_2, angle_symm_2 = single_symmetry(self.lp_re_2, calc_pt_list)
                dist_symm_3, angle_symm_3 = single_symmetry(self.lp_re_3, calc_pt_list)

                self.log_something('#1')
                self.log_something(' -    D.S.S:  %.2f' % dist_symm_1)
                self.log_something(' -    A.S.S:  %.2f' % angle_symm_1)
                self.log_something('#2')
                self.log_something(' -    D.S.S:  %.2f' % dist_symm_2)
                self.log_something(' -    A.S.S:  %.2f' % angle_symm_2)
                self.log_something('#3')
                self.log_something(' -    D.S.S:  %.2f' % dist_symm_3)
                self.log_something(' -    A.S.S:  %.2f' % angle_symm_3)
            else:
                self.log_something('Check the combo box')
            
            self.log_something('\n')
        except:
            self.log_something('Fail\n')

        
    def log_something(self, log_txt):
        # plainTextEdit에 로그 출력
        self.log_edit.appendPlainText(log_txt)

    def resizeEvent(self, e):
        try:
            if self.load_selected:
                if not self.img_view_flag:
                    return
        
                self.draw_Mark()
            else:
                self.img_print.setStyleSheet("background-color: rgb(0, 0, 0);color: rgb(255, 255, 255);")
        except:
            QMessageBox.warning(self, "경고", "창 크기 조절 오류", QMessageBox.Ok)
            None

    def closeEvent(self, event):

        # 홈으로 이동
        main_window.show()
        self.close()


class Window_Dynamic(QMainWindow, dynamic_page):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # MediaPipe 검출기 생성 매개변수
        max_num_faces = 1
        min_detection_confidence = 0.7
        min_tracking_confidence = 0.5
        model_complexity = 1

        # MediaPipe face mesh 검출기 생성
        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            refine_landmarks=True,
        )

        # Video player
        self.vd_name = ''
        self.video_loaded = False
        self.play = False
        self.ld_view_toggle = False

        # Button connections
        self.play_btn.clicked.connect(self.vdPlay)
        # self.pause_btn.clicked.connect(self.pause)
        self.stop_btn.clicked.connect(self.stop)
        self.vd_load_btn.clicked.connect(self.load_video)
        self.ld_view_btn.clicked.connect(self.ld_view)

        # 슬라이더
        self.vd_slider.sliderMoved.connect(self.set_position)
        self.vd_slider.setEnabled(False)

        # # 저장
        # self.Save_btn.clicked.connect(self.saveFunc)

        self.thread = VdAnalysis()
        self.thread.finished_signal.connect(self.on_thread_finished)
        self.analysis_s_btn.clicked.connect(self.analysis_start)

        # 비디오 파일의 총 프레임 수 및 FPS
        self.total_frames = 1
        self.fps = 0
        self.c_loc = 0

        #landmark 설정
        self.p_size = 1
        self.spinBox.setMinimum(1)
        self.spinBox.setValue(1)
        self.spinBox.valueChanged.connect(self.spin_handle)

        self.setcolor = (0, 0, 255)
        self.cb_color.addItems(['Red', 'Blue', 'Green'])
        self.cb_color.setCurrentText('Blue')
        self.cb_color.activated.connect(self.cb_handle)

        self.timeq = QtCore.QTimer()
        self.timeq.timeout.connect(self.mediaUpdate)
    
    def selected_landmark(self, selected_landmarks):
        self.select_num_list = selected_landmarks
        # self.log_something(f'Select Landmark List : {len(self.select_num_list)}\n{self.select_num_list}\n')
        self.log_something(f'Select Landmark List : {len(self.select_num_list)}')
    
    def cb_handle(self, value):

        selected_item = self.cb_color.currentText()
        
        color_blue = (0, 0, 255)
        color_red = (255, 0, 0)
        color_green = (0, 255, 0)

        if selected_item == 'Red':
            self.setcolor = color_red
        elif selected_item == 'Blue':
            self.setcolor = color_blue
        elif selected_item == 'Green':
            self.setcolor = color_green
        else:
            self.log_something("color err")
        
        if not self.video_loaded:
            return

        self.draw_pixmap(self.frame, self.vd_print)

    def spin_handle(self, value):

        self.p_size = value

        if not self.video_loaded:
            return
        self.draw_pixmap(self.frame, self.vd_print)
    
    def ld_view(self):
        if not self.video_loaded:
            return

        self.ld_view_toggle = not self.ld_view_toggle
        self.draw_pixmap(self.frame, self.vd_print)

    def load_video(self):
        try:
            self.vd_name = QFileDialog.getOpenFileName(self, 'Load Video', '',
                                                       'Videos (*.avi *.mp4 *.mov *.mkv);;All Files (*)')
            if self.vd_name[0]:
                
                self.video = cv2.VideoCapture(self.vd_name[0])

                link_list = self.vd_name[0].split('/')
                # fname = link_list[len(link_list) - 1][:-4]
                fname = link_list[len(link_list) - 1]
                self.fname_label.setText('%s' % fname)

                # 비디오 파일의 총 프레임 수 및 FPS를 가져옵니다.
                self.total_frames = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.video.get(cv2.CAP_PROP_FPS)
                self.frame_duration = round(1000 / int(self.fps))

                # minutes, ms = divmod(self.total_frames * self.frame_duration, 60000)
                # hours, minutes = divmod(minutes, 60)
                # seconds = ms // 1000

                self.video_loaded = True

                # slider
                self.vd_slider.setRange(0, self.total_frames - 1)
                self.vd_slider.setValue(0)
                self.vd_slider.setEnabled(True)
                
                # 전체 재생 시간 계산
                total_seconds = int(self.total_frames / self.fps)
                # 초를 시분초 형태로 변환
                self.total_time = sec_to_time(total_seconds)
                self.c_loc = 0
                self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.mediaUpdate()

        except Exception as e:
            # QMessageBox.warning(self, "Warning", str(e))
            self.log_something("영상을 다시 업로드 해주세요")
            traceback.format_exc()

    def vdPlay(self):
        try:
            if not self.video_loaded:
                return

            if self.video.isOpened():
                if self.play:
                    self.play = False
                    self.timeq.stop()
                    self.play_btn.setText('▶')
                else:
                    self.play = True
                    self.timeq.start(self.fps)
                    self.play_btn.setText('||')
        except:
            QMessageBox.warning(self, "경고", "영상 재생이 안됩니다!", QMessageBox.Ok)
            self.log_something("영상 재생이 정상적으로 되지 않습니다!")
            traceback.format_exc()

    # def pause(self):
    #     try:
    #         if not self.video_loaded:
    #             return

    #         if self.video.isOpened():
    #             self.play = False
    #             self.timeq.stop()
    #     except:
    #         # QMessageBox.warning(self, "경고", "영상 일시정지 오류!", QMessageBox.Ok)
    #         self.log_something("일시정지가 정상적으로 되지 않습니다!")
    #         traceback.format_exc()

    def stop(self):
        try:
            if not self.video_loaded:
                return

            if self.video.isOpened():
                self.play = False
                self.timeq.stop()
                self.c_loc = 0
                self.vd_slider.setValue(self.c_loc)
                self.video.set(cv2.CAP_PROP_POS_FRAMES, self.c_loc)
                self.mediaUpdate()
                self.play_btn.setText('▶')
        except:
            # QMessageBox.warning(self, "경고", "영상 정지 오류!", QMessageBox.Ok)
            self.log_something("영상 정지가 정상적으로 되지 않습니다!")
            traceback.format_exc()
    
    def set_position(self):
        self.c_loc = int(self.vd_slider.value())
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.c_loc)
        self.mediaUpdate()
   
    def analysis_start(self):
        self.log_something(f"{self.fname_label.text()} is loaded.")
        self.log_something("wait…")
        # self.log_something("영상의 길이와 해상도 크기에 따라 분석이 길어질 수 있습니다.")
        self.thread.start_with(self.vd_name[0], self.select_num_list)
    
    def log_something(self, log_txt):
        # plainTextEdit에 로그 출력
        self.log_edit.appendPlainText(log_txt)
    
    def resizeEvent(self, e):
        try:
            if self.video_loaded:
                self.draw_pixmap(self.frame, self.vd_print)
        except:
            QMessageBox.warning(self, "경고", "창 크기 조절 중 오류가 났습니다.!", QMessageBox.Ok)
            None

    def draw_pixmap(self, image, label):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = image.shape
        
        # 랜드마크 계산
        if self.ld_view_toggle:
            results = self.face_mesh.process(image)

            if results.multi_face_landmarks is not None:
                for face_landmarks in results.multi_face_landmarks:
                    image = draw_landmarks(image, face_landmarks, self.setcolor, self.p_size)
        else:
            pass

        cimage = QtGui.QImage(image.data, w, h, ch * w, QtGui.QImage.Format_RGB888)
        scaled_pixmap = QtGui.QPixmap.fromImage(cimage).scaled(label.size(), QtCore.Qt.KeepAspectRatio)
        label.setPixmap(scaled_pixmap)
        label.setAlignment(QtCore.Qt.AlignCenter)

    # 영상 업데이트 함수
    def mediaUpdate(self):
        try:
            if self.play:
                self.vd_slider.setValue(self.c_loc)
                self.c_loc += 1

            ret, self.frame = self.video.read(cv2.CAP_DSHOW)
            if not ret:
                self.play = False
                self.timeq.stop()
                self.frame = self.prnt_frame
                self.play_btn.setText('▶')
                return

            self.prnt_frame = self.frame.copy()
            self.draw_pixmap(self.prnt_frame, self.vd_print)

            current_time_txt = sec_to_time(self.c_loc / self.fps)
            self.time_chk.setText(f"{current_time_txt}/{self.total_time}")

        except Exception as e:
            # QMessageBox.warning(self, "경고", "영상 로딩 오류!", QMessageBox.Ok)
            self.log_something("영상 로딩 오류!")
            traceback.format_exc()
            raise

    def on_thread_finished(self, result):
        # TODO : 작업 결과를 처리하는 코드를 여기에 구현합니다.
        now = datetime.now() # 현재 시간을 가져옵니다.
        current_date = now.strftime("%B %d, %Y")
        current_time = now.strftime("%H:%M") # 시간을 hh:mm 형식으로 포맷합니다.
        self.log_something(f"\nHere is the result of the analysis at {current_time} on {current_date}. This shows the movement symmetry scores (M.S.S).")
        self.log_something('\n')

        self.sv_result = result

        # 부위별 결과
        result_areas = ['eye', 'eyebrow', 'cheek', 'mouth']
        f_areas = ['Eye', 'Eye Brow', 'Cheek', 'Mouth']
        for i, t0 in enumerate(result_areas):
            area_str = "- {}: {:05.2f} ( {:05.2f} / {:05.2f} / {:05.2f} / {:05.2f} )"
            row = area_str.format(
                f_areas[i],
                result["Symmetry " + t0],
                result[f"{t0} left"],
                result[f"{t0} right"],
                result[f"{t0} left (max)"],
                result[f"{t0} right (max)"],
            )
            self.log_something(row)
        self.log_something('\n')

        # 4area 결과
        areas = ['area0_green', 'area1_blue', 'area2_yellow', 'area3_red']
        for i, t0 in enumerate(areas):
            area_str = "- Area{}: {:05.2f} ( {:05.2f} / {:05.2f} / {:05.2f} / {:05.2f} )"
            row = area_str.format(
                i,
                result["Symmetry " + t0],
                result[f"{t0} left"],
                result[f"{t0} right"],
                result[f"{t0} left (max)"],
                result[f"{t0} right (max)"],
            )
            self.log_something(row)
        self.log_something('\n')

        # 선택 영역 결과
        areas = ['Selected']
        for i, t0 in enumerate(areas):
            area_str = "- {}: {:05.2f} ( {:05.2f} / {:05.2f} / {:05.2f} / {:05.2f} )"
            row = area_str.format(
                'Selected',
                result["Symmetry " + t0],
                result[f"{t0} left"],
                result[f"{t0} right"],
                result[f"{t0} left (max)"],
                result[f"{t0} right (max)"],
            )
            self.log_something(row)
        self.log_something('\n')
    
    # # TODO
    # def saveFunc(self):
    #     self.log_something('Currently under construction')

    #     # # 4area 결과 저장
    #     # root_path = './'
    #     # file_name = self.fname_label.text()
    #     # f = open(root_path + file_name + '_result.csv', 'w', newline='')
    #     # writer = csv.writer(f)

    #     # writer.writerow(['', 'Symmetry', 'left', 'right', 'left_max', 'right_max'])        
        
    #     # for t0 in v_calc.areas:
    #     #     writer.writerow([t0, '%.2f' % v_calc.result['Symmetry ' + t0], '%.2f' % v_calc.result[f'{t0} left'], '%.2f' % v_calc.result[f'{t0} right'], '%.2f' % v_calc.result[f'{t0} left (max)'], '%.2f' % v_calc.result[f'{t0} right (max)']])
        
    #     # f.close()
        
    def closeEvent(self, event):

        # 홈으로 이동
        main_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    main_window = Window_1st()
    # main_window.show()
    main_window.show()
    
    select_window = PtSelectWin()
    static_window = Window_Static()
    dynamic_window = Window_Dynamic()

    app.exec_()