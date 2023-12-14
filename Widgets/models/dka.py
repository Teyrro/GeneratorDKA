from PyQt5.QtCore import QObject
from pandas import DataFrame


def get_compute_multi_branch() -> tuple:
    return (
        lambda *argc: ((argc[0] + argc[1]) % argc[2]) * argc[3] + 1,
        lambda *argc: ((argc[0] + 1 + argc[1]) % argc[2]) * argc[3],
    )


def get_compute_one_branch() -> tuple:
    return lambda *argc: 1, lambda *argc: 0


def get_compute_func(m):
    m_funcs = {"one": get_compute_one_branch, "multi": get_compute_multi_branch}
    return m_funcs[m]()


def add_edge(dt: DataFrame, start_state: str, end_state: str, name_edge: str):
    if dt[name_edge][start_state] == "":
        dt[name_edge][start_state] = end_state


class DKA(QObject):
    """
    DKA model, generate dka by alphabet setting
    """

    def __init__(self, parent, access_sym=None, subchain=None, multiplicity=None):
        super().__init__(parent)
        self.multiplicity = None
        self.subchain = None
        self.access_sym = None
        self.m_name: str | None = None
        self.set_info(access_sym, subchain, multiplicity)

        self.start_state: str | None = None
        self.end_state: str | None = None
        self._dt: DataFrame | None = None

    def set_info(self, symbols: str, subchain: str = "", multiplicity: str = "1"):
        """
        Set up params
        :param symbols:
        :param subchain:
        :param multiplicity:
        :return: None
        """
        self.access_sym = symbols
        self.subchain = subchain
        if multiplicity is not None and multiplicity != 0:
            self.multiplicity = int(multiplicity)
        if self.multiplicity == 1:
            self.m_name = "one"
        else:
            self.m_name = "multi"

    def generate_background_part(self, dt: DataFrame, name: str, mult: int) -> None:
        """
        Generate nodes circulant subgraph
        :param dt:
        :param name:
        :param mult:
        :return: None
        """
        for i in range(0, -mult, -1):
            if i == 0:
                ss = name + str(-mult)
            else:
                ss = name + str(i)
            if i - 1 == -mult:
                es = name + str(-mult)
            else:
                es = name + str(i - 1)
            for char in self.access_sym:
                add_edge(dt, ss, es, char)

    def create_dt(self, name_state: str, mult: int) -> DataFrame:
        """
        Create table with columns and indexes
        :param name_state:
        :param mult:
        :return: DataFrame
        """

        states: list[str] = []
        for i in range(-1, -mult - 1, -1):
            states.append(name_state + str(i))

        subchain_size = len(self.subchain)
        start_pos = end_pos = 0
        for i in range(mult):
            end_pos += subchain_size
            for j in range(start_pos, end_pos):
                states.append(name_state + str(j))
            start_pos += subchain_size
        return DataFrame("", states, list(self.access_sym))

    def create_dka(self) -> None:
        """
        Generate dka

        In loop generate branches, every iteration is branch
        with nodes count == max(subchain_size, mult)
        (iteration count == len(multiplicity))

        :return: None
        """
        name = "q"

        mult: int = int(self.multiplicity)
        dt = self.create_dt(name, mult)

        subchain_size = len(self.subchain)
        # branch_size = max(subchain_size, mult)

        self.generate_background_part(dt, name, mult)
        if subchain_size == 0:
            self.start_state = name + str(-1)
        else:
            self.start_state = name + str(0)

        self.end_state = name + str(-mult)
        for num_branch in range(mult):
            offset = num_branch * subchain_size
            self.generate_subchain_part(dt, num_branch, offset, name, subchain_size)
            self.generate_other_ways(dt, name, num_branch, subchain_size)

        # print(dt)
        self._dt = dt

    def generate_other_ways(
        self,
        dt: DataFrame,
        name: str,
        num_branch: int,
        subchain_size: int,
    ) -> None:
        """
        Other ways are computed depends on number in branch % subchain * branch_size
        almost to all case.

        If current char isn't first in subchain, example above suit us
        other functions in \'get_compute_one\', \'get_compute_multi\'
        :param dt:
        :param name:
        :param num_branch:
        :param subchain_size:
        :return:  None
        """
        if subchain_size == 0:
            return

        compute_func: tuple = get_compute_func(self.m_name)
        start_char: str = self.subchain[0]
        for i in range(subchain_size):
            index = i + num_branch * subchain_size
            state_name = name + str(index)
            for cur_char in self.access_sym:
                if dt[cur_char][state_name] == "":
                    check_neq = cur_char != start_char
                    get_ind = compute_func[check_neq]
                    ind = get_ind(i, num_branch, self.multiplicity, subchain_size)
                    ss = state_name
                    es = name + str(ind)
                    add_edge(dt, ss, es, cur_char)

    def generate_subchain_part(
        self,
        dt: DataFrame,
        number_branch: int,
        offset: int,
        name: str,
        subchain_size: int,
    ) -> None:
        """
        Generates relates between nodes of subchain, only main relates.
        Offset == subchain size * number branch
        :param dt:
        :param number_branch:
        :param offset:
        :param name:
        :param subchain_size:
        :return: None
        """
        for ind, it in enumerate(self.subchain):
            index = ind + offset
            ss = name + str(index)
            if ind != len(self.subchain) - 1:
                es = name + str(index + 1)
            else:
                index = (number_branch + subchain_size) % int(self.multiplicity)
                if index == 0:
                    index += int(self.multiplicity)
                es = name + str(-index)
            add_edge(dt, ss, es, it)

    @property
    def dt(self) -> DataFrame | None:
        if self._dt is None:
            return None
        return self._dt.copy(deep=True)
