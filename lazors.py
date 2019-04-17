import pylazors
import glob
import os
import time


board_dir = 'boards'
solution_dir = 'solutions'


def solve_all(boards, save_img=True):
    """
    Solve a list of boards, print timing information, and return solution boards.
    """

    time_history = []
    solutions = []

    for board in boards:
        print('\n[solve_all] start board solving for', board)

        start_time = time.time()
        solution_board = pylazors.solve_board(board)
        solutions.append(solution_board)
        time_used = time.time() - start_time
        time_history.append((solution_board.name, time_used))

        if solution_board is not None:
            print('[solve_all] solution found in %f seconds' % time_used)
            print('[solve_all] solution:', solution_board.get_blocks())
            if save_img:
                img_name = os.path.join(solution_dir, solution_board.name + '.png')
                note = 'solved in %.3f seconds' % time_used
                pylazors.write_png(solution_board, img_name, note)
                print('[solve_all] solution saved to %s.' % img_name)
        else:
            print('[solve_all] No solution found after testing all possible combinations, time used: %f seconds' % time_used)

    print('\n[solve_all] All jobs done.')
    t_list = [x[1] for x in time_history]
    t_sum, t_min, t_max = sum(t_list), min(t_list), max(t_list)

    print('[solve_all] %d boards solved in %.3f seconds (min/avg/max %.3f/%.3f/%.3f).' % (
        len(boards), t_sum, t_min, t_sum / len(boards), t_max))
    if len(boards) > 5:
        top_5 = list(reversed(sorted(time_history, key=lambda x: x[1])))[:5]
        print('[solve_all] 5 slowest boards: ' + ', '.join(['%s (%.1fs)' % h for h in top_5]))

    return solutions


if __name__ == '__main__':

    all_boards = []
    for bff_file in sorted(glob.glob(os.path.join(board_dir, 'handout', '*.bff'))):
        all_boards.append(pylazors.read_bff(bff_file))
        print('[main] load board:', all_boards[-1])
    print('[main] %d boards loaded.' % len(all_boards))

    solve_all(all_boards)
