# typer
A minimal type inferencer

```
 ↳ python test.py
Unify Type 1 and Type 2:

Type 1  -> (* ('a1 -> 'a2) (list 'a3)) -> list 'a2
Type 2  -> (* ('a3 -> 'a4) (list 'a3)) -> 'a5

Slot map: {'a2: 'a4, 'a1: 'a3, 'a5: list 'a4}

Unifed result:  apply 1 -> (* ('a3 -> 'a4) (list 'a3)) -> list 'a4
Unifed result:  apply 2 -> (* ('a3 -> 'a4) (list 'a3)) -> list 'a4

Some inference examples are defined in test.py, there is inference result:

{'+': int -> int -> int,
 '0': int,
 '1': int,
 'call': forall 'a 'b. ('a -> 'b) -> 'a -> 'b,
 'car': forall 'a. (list 'a) -> 'a,
 'cdr': forall 'a. (list 'a) -> list 'a,
 'cons': forall 'a. 'a -> (list 'a) -> list 'a,
 'crz': forall 'a 'b 'c. 'a -> 'b -> 'c -> 'c,
 'empty?': forall 'a. (list 'a) -> bool,
 'hold': forall 'a. 'a -> thunk 'a,
 'if': forall 'a. bool -> (thunk 'a) -> (thunk 'a) -> 'a,
 'length': forall 'a. (list 'a) -> int,
 'map': forall 'a 'b. ('b -> 'a) -> (list 'b) -> list 'a,
 'newlist': forall 'a. unit -> list 'a,
 'nothing': unit,
 'seq': forall 'a 'b. 'a -> 'b -> 'b,
 'sum': forall. (list int) -> int}
```
