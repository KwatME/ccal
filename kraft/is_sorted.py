from numpy import diff


def is_sorted_array(array):

    diff_ = diff(array)

    return (diff_ <= 0).all() or (0 <= diff_).all()