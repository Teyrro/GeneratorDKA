from dataclasses import dataclass, field

from pandas import DataFrame


@dataclass
class DKA:
    access_sym: str = field(default=None, init=False)
    subchain: str = field(default=None, init=False)
    multiplicity: int = field(default=None, init=False)
    start_state: str = field(default=None, init=False)
    end_state: str = field(default=None, init=False)
    _dt: DataFrame = field(default=None, init=False)

    def set_info(self, symbols: str, subchain: str = "", multiplicity: str = "1"):
        self.access_sym = symbols
        self.subchain = subchain
        self.multiplicity = int(multiplicity)

    def generate_background_part(self, dt, name: str, mult):
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
                self.add_edge(dt, ss, es, char)

    def create_dt(self, name_state: str, mult: int):
        def count_state(m, subchain_size):
            l: list[int] = []
            if m == 0:
                return [0]
            for _ in range(0, m):
                l.append(subchain_size)
            return l

        state_count = count_state(mult, len(self.subchain))
        states: list[str] = []
        # if len(state_count) > 1:
        for i in range(-1, -mult - 1, -1):
            states.append(name_state + str(i))
        start_pos = end_pos = 0
        for i in state_count:
            end_pos += i
            for j in range(start_pos, end_pos):
                states.append(name_state + str(j))
            start_pos += i
        return DataFrame("", states, list(self.access_sym))

    def create_dka(self):
        name = "q"

        mult: int = int(self.multiplicity)
        dt = self.create_dt(name, mult)
        # print(dt)
        # print(dt.info())

        subchain_size = len(self.subchain)
        branch_size = max(subchain_size, mult)
        print(f"branch_size: {branch_size}\n"
              f"subchain_size: {subchain_size}\n"
              f"mult: {mult}")
        self.generate_background_part(dt, name, mult)
        if subchain_size == 0:
            self.start_state = name + str(-1)
        else:
            self.start_state = name + str(0)

        self.end_state = name + str(-mult)
        for num_branch in range(mult):
            offset = num_branch * subchain_size
            self.generate_subchain_part(dt, num_branch, offset, name, subchain_size)
            self.generate_other_ways(dt, name, num_branch, subchain_size, branch_size)

        print(dt)
        self._dt = dt
        # return dt.copy(deep=True)

    @staticmethod
    def add_edge(dt: DataFrame, start_state: str, end_state: str, name_edge: str):
        if dt[name_edge][start_state] == "":
            dt[name_edge][start_state] = end_state

    def generate_other_ways(self, dt: DataFrame, name: str, num_branch: int,
                            subchain_size: int, branch_size: int):

        get_ind_if_a = lambda *argc: ((argc[0] + argc[1]) % argc[2]) * argc[3] + 1
        get_ind_if_other = lambda *argc: ((argc[0] + 1 + argc[1]) % argc[2]) * argc[3]
        if self.multiplicity == 1 and subchain_size > 0:
            get_ind_if_a = lambda *argc: 1
            get_ind_if_other = lambda *argc: 0

        for i in range(subchain_size):
            index = i + num_branch * subchain_size
            state_name = name + str(index)
            for j in self.access_sym:
                if dt[j][state_name] == "":

                    if self.subchain[0] == j:
                        ind = get_ind_if_a(i, num_branch, self.multiplicity, subchain_size)
                    else:
                        ind = get_ind_if_other(i, num_branch, self.multiplicity, subchain_size)

                    ss = state_name
                    es = name + str(ind)
                    print(f"start_state: {state_name} to: {es}\n"
                          f"i: {i}, num_branch: {num_branch}, branch: {branch_size}, subchain: {subchain_size}"
                          f"ind: {ind}")
                    self.add_edge(dt, ss, es, j)

    def generate_subchain_part(self, dt: DataFrame, number_branch: int,
                               offset: int, name: str, subchain_size: int):
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
            self.add_edge(dt, ss, es, it)

    @property
    def dt(self):
        if self._dt is None:
            return None
        return self._dt.copy(deep=True)
