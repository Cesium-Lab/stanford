import numpy as np


def box_iou(a, b):
    """
    Pairwise intersection over union of boxes in (x1, y1, x2, y2) format.
    Inputs:
        a: (N, 4), b: (M, 4)
    Output:
        (N, M) array, entry [i, j] is IoU(a[i], b[j])

    HINT: broadcast a[:, None, :] against b[None, :, :]; no for-loops needed.
    """
    ########## Code starts here ##########
    
    # Did in fact use chat for broadcasting here
    b1 = a[:, None, :]
    b2 = b[None, :, :]
        
    # 
    x_left = np.maximum(b1[...,0], b2[...,0])
    y_bottom = np.maximum(b1[...,1], b2[...,1])
    x_right = np.minimum(b1[...,2], b2[...,2])
    y_top = np.minimum(b1[...,3], b2[...,3])
    
    width = np.maximum(0, x_right - x_left)
    height = np.maximum(0, y_top - y_bottom)
    box = width*height
    
    A1 = (b1[...,2]-b1[...,0])*(b1[...,3]-b1[...,1])
    A2 = (b2[...,2]-b2[...,0])*(b2[...,3]-b2[...,1])
    
    union = A1 + A2 - box

    return np.divide(box, union,
                        out=np.zeros_like(box, dtype=float), 
                        where=union > 0)
    ########## Code ends here ##########


def nms(boxes, scores, iou_threshold):
    """
    Greedy non-maximum suppression.
    Inputs:
        boxes: (N, 4), scores: (N,)
        iou_threshold: a box is removed if its IoU with a higher-scoring kept box is > iou_threshold
    Output:
        (K,) integer indices of the kept boxes, sorted by decreasing score
    """
    ########## Code starts here ##########
    
    idx_ordered = np.argsort(scores)[::-1]
    
    F = []

    while len(idx_ordered) > 0:
    
        idx = idx_ordered[0]
        F.append(idx)
        
        remaining = idx_ordered[1:]

        ious = box_iou(boxes[idx:idx+1], boxes[remaining]).reshape(-1)

        # Remove boxes exceeding IoU threshold
        idx_ordered = remaining[ious <= iou_threshold]
        
    return np.array(F, dtype=int)
    ########## Code ends here ##########


def batched_nms(boxes, scores, labels, iou_threshold):
    """
    NMS applied separately within each class label, so boxes of different
    classes never suppress each other.
    Output:
        (K,) integer indices of the kept boxes over all classes, sorted by decreasing score
    """
    ########## Code starts here ##########
    
    idx_range = np.arange(len(scores))
    filtered_idx = []
    filtered_scores = []
    for lab in set(labels):
        idx = nms(boxes[labels == lab], scores[labels == lab], iou_threshold)

        filtered_idx = np.concatenate((filtered_idx, idx_range[labels == lab][idx]))
        filtered_scores = np.concatenate((filtered_scores, scores[labels == lab][idx]))

    return np.array([int(x) for x in filtered_idx[np.argsort(filtered_scores)[::-1]]])
    ########## Code ends here ##########


def match_detections(boxes, scores, gt_boxes, iou_threshold=0.5):
    """
    Labels each detection as a true positive or a false positive.
    Detections are processed in decreasing score order. Each one is matched to
    the ground-truth box it overlaps most; it is a true positive if that IoU is
    >= iou_threshold and that ground-truth box has not been matched yet,
    otherwise it is a false positive.
    Inputs:
        boxes: (N, 4), scores: (N,), gt_boxes: (G, 4)
    Output:
        (N,) boolean array aligned with the input order (True = true positive)
    """
    ########## Code starts here ##########
    iou_grid = box_iou(boxes, gt_boxes)  # (N,G)
    # print(iou_grid)
    scores = scores.copy()
    
    # (G,)
    available_gt = np.ones(len(gt_boxes), dtype=bool)
    found_scores = np.zeros(len(scores), dtype=bool)
    
    for s_i in np.argsort(-scores):

        # highest iou
        gt_i = np.argmax(iou_grid[s_i])

        if (
            iou_grid[s_i, gt_i] >= iou_threshold
            and available_gt[gt_i]
        ):
            available_gt[gt_i] = False
            found_scores[s_i] = True

    return found_scores
    ########## Code ends here ##########


def precision_recall(scores, tp, num_gt):
    """
    Precision and recall when keeping the top-k detections, for k = 1, ..., N.
    Inputs:
        scores: (N,), tp: (N,) boolean from match_detections, num_gt: number of ground-truth boxes
    Output:
        precision, recall: (N,) arrays, entry k-1 uses the k highest-scoring detections
    """
    ########## Code starts here ##########
    idx = np.argsort(-scores)
    tp_sorted = tp[idx]
    
    true_pos = 0
    precision = []
    recall = []
    
    for i,b in enumerate(tp_sorted):
        if b:
            true_pos += 1
        
        precision.append(true_pos/(i+1))
        recall.append(true_pos/num_gt if num_gt > 0 else 0.0)

    return np.asarray(precision), np.asarray(recall)
    ########## Code ends here ##########


def average_precision(precision, recall):
    """
    All-point interpolated average precision (area under the PR curve), where the
    precision at each recall is replaced by the maximum precision at any higher recall.
    Inputs:
        precision, recall: (N,) arrays from precision_recall
    Output:
        float AP in [0, 1]
    """
    ########## Code starts here ##########
    if len(precision) == 0:
        return 0.0

    # Interpolated precision envelope
    p_interp = np.maximum.accumulate(precision[::-1])[::-1]
    print(p_interp)

    # Change in recall at each detection
    dr = np.diff(np.r_[0, recall])

    return float(np.sum(p_interp * dr))
    # new_p = []
    # for i,(p,r) in enumerate(zip(precision, recall)):
    #     high = precision[recall > recall[i]]
        # new_p.append()
    p_new = [
        precision[np.argmax(precision[recall >= recall[i]])] for i,p in enumerate(precision)
    ]
    print(p_new)
    return np.cumsum(p_new)
    ########## Code ends here ##########
