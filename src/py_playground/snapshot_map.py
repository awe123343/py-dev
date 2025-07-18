# ruff: noqa: T201

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class HistoryEntry:
    """A Plain Old Python Object to store a value at a specific snapshot moment."""

    snap_id: int
    value: int | None


class SnapshottableMap:
    """
    A map-like class that supports taking snapshots of its state.

    This implementation records the history of each key as it's modified.
    The `put` and `take_snapshot` operations are O(1). Getting from a snapshot
    is O(log S) via binary search.

    Raises:
        KeyError: If a key is not found in the map or in a specified snapshot.
    """

    def __init__(self) -> None:
        """
        Initializes the SnapshottableMap.
        """
        # Maps a key to its value history using the HistoryEntry class.
        self._key_history_store: dict[str, list[HistoryEntry]] = {}

        # A counter to generate unique, sequential snapshot IDs, starting from 0.
        self._next_snap_id: int = 0

    def take_snapshot(self) -> int:
        """
        Captures the current state and returns a snapshot ID. O(1) complexity.

        Returns:
            A new, unique snapshot ID (int).
        """
        snap_id: int = self._next_snap_id
        self._next_snap_id += 1
        return snap_id

    def put(self, k: str, v: int | None) -> None:
        """
        Associates a value with a key, recording the change for the next snapshot.

        Args:
            k: The key (str).
            v: The value (int or None for deletion).
        """
        history: list[HistoryEntry] = self._key_history_store.setdefault(k, [])

        # If a change was already logged for this key before the next snapshot,
        # just update the value. Otherwise, append a new entry.
        if history and history[-1].snap_id == self._next_snap_id:
            history[-1].value = v
        else:
            history.append(HistoryEntry(snap_id=self._next_snap_id, value=v))

    def delete(self, k: str) -> None:
        """
        Records the deletion of a key for the next snapshot.

        Args:
            k: The key (str) to delete.
        """
        if k in self._key_history_store:
            self.put(k, None)

    def get(self, k: str) -> int:
        """
        Returns the current value for a given key. This is an O(1) operation.

        Args:
            k: The key whose associated value is to be returned.

        Returns:
            The current value associated with the key.
        """
        history: list[HistoryEntry] | None = self._key_history_store.get(k)
        if not history:
            msg = f"Key '{k}' not found in current map state."
            raise KeyError(msg)

        latest_value: int | None = history[-1].value
        if latest_value is None:
            msg = f"Key '{k}' not found (it may have been deleted)."
            raise KeyError(msg)
        return latest_value

    def get_from_snapshot(self, k: str, snap_id: int) -> int | None:
        """
        Returns the value for a key from a specific historical snapshot.

        Args:
            k: The key whose associated value is to be returned.
            snap_id: The ID of the snapshot to retrieve from.

        Returns:
            The value associated with the key in the specified snapshot.
        """
        if not (0 <= snap_id < self._next_snap_id):
            valid_range: str = (
                "No snapshots taken yet." if self._next_snap_id == 0 else f"0 to {self._next_snap_id - 1}."
            )
            msg = f"Invalid snap_id: {snap_id}. {valid_range}"
            raise IndexError(msg)

        history: list[HistoryEntry] | None = self._key_history_store.get(k)
        if not history:
            msg = f"Key '{k}' never existed, so it's not in snapshot {snap_id}."
            raise KeyError(msg)

        # Perform a manual binary search on the history list to find the relevant
        # snapshot without creating an intermediate list. This is O(log S).
        left, right = 0, len(history) - 1
        # `idx` will store the index of the last version of the key at or before the snapshot.
        idx = -1

        while left <= right:
            mid = (left + right) // 2
            # Compare with the snapshot ID of the HistoryEntry object.
            if history[mid].snap_id <= snap_id:
                idx = mid
                left = mid + 1
            else:
                right = mid - 1

        if idx == -1:
            logger.error("Key '%s' did not exist in snapshot %s.", k, snap_id)

            return None

        relevant_value: int | None = history[idx].value
        if relevant_value is None:
            msg = f"Key '{k}' did not exist in snapshot {snap_id} (it was deleted)."
            raise KeyError(msg)

        return relevant_value


if __name__ == "__main__":
    s = SnapshottableMap()
    s.put("1", 1)
    s.put("2", 2)
    s.put("3", 3)
    print(s.take_snapshot())  # snapshot_id 0

    s.put("1", 2)
    print(s.take_snapshot())  # snapshot_id 1

    s.put("4", 4)
    s.put("3", 4)
    print(s.take_snapshot())  # snapshot_id 2

    print("---")
    print(s.get_from_snapshot("1", 0))
    print(s.get_from_snapshot("1", 1))
    print(s.get_from_snapshot("1", 2))
    print("---")
    print(s.get_from_snapshot("4", 0))
    print(s.get_from_snapshot("4", 1))
    print(s.get_from_snapshot("4", 2))
