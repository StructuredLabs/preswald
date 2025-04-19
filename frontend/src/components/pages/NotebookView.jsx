import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';
import CodeMirror from '@uiw/react-codemirror';
import { v4 as uuidv4 } from 'uuid';

import React, { useCallback, useEffect, useState } from 'react';
import { DragDropContext, Draggable, Droppable } from 'react-beautiful-dnd';

import { Alert } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

import { comm } from '@/utils/websocket';

import HTMLRenderer from '../common/HTMLRenderer';

const NotebookView = () => {
  // Each cell holds its id, code, output, status, error, and whether it’s been executed.
  const [cells, setCells] = useState([
    { id: uuidv4(), code: '', output: '', status: 'idle', error: null, executed: false },
  ]);

  // Subscribe to WebSocket messages to update cell outputs and restore state.
  useEffect(() => {
    const unsubscribe = comm.subscribe((message) => {
      if (message.type === 'notebook_state' && message.cells) {
        // On refresh, clear the executed flag on all cells.
        const resetCells = message.cells.map((cell) => ({ ...cell, executed: false }));
        setCells(resetCells);
      }
      if (message.type === 'cell_result' && message.cell_id) {
        setCells((prevCells) => {
          const updatedCells = prevCells.map((cell) =>
            cell.id === message.cell_id
              ? {
                  ...cell,
                  output: message.output,
                  status: message.error ? 'error' : 'idle',
                  error: message.error || null,
                  executed: true,
                }
              : cell
          );
          // Optionally persist this updated state to the server if needed.
          comm.send({ type: 'update_notebook', cells: updatedCells });
          return updatedCells;
        });
      }
    });
    return () => unsubscribe();
  }, []);

  // Run a cell: send code via WebSocket and mark cell as running.
  const runCell = useCallback(
    (cellId) => {
      setCells((prevCells) =>
        prevCells.map((cell) =>
          cell.id === cellId
            ? { ...cell, status: 'running', output: '', error: null, executed: false }
            : cell
        )
      );
      const cell = cells.find((c) => c.id === cellId);
      if (cell) {
        comm.send({ type: 'run_cell', cell_id: cell.id, code: cell.code });
      }
    },
    [cells]
  );

  // Update cell code and notify the server.
  const updateCellCode = (cellId, newCode) => {
    setCells((prevCells) => {
      const updatedCells = prevCells.map((cell) =>
        cell.id === cellId ? { ...cell, code: newCode, executed: false } : cell
      );
      comm.send({ type: 'update_notebook', cells: updatedCells });
      return updatedCells;
    });
  };

  // Append a new cell.
  const addCell = () => {
    const newCell = {
      id: uuidv4(),
      code: '',
      output: '',
      status: 'idle',
      error: null,
      executed: false,
    };
    setCells((prevCells) => {
      const updatedCells = [...prevCells, newCell];
      comm.send({ type: 'update_notebook', cells: updatedCells });
      return updatedCells;
    });
  };

  // Remove a cell.
  const deleteCell = (cellId) => {
    setCells((prevCells) => {
      const updatedCells = prevCells.filter((cell) => cell.id !== cellId);
      comm.send({ type: 'update_notebook', cells: updatedCells });
      return updatedCells;
    });
  };

  // Handle drag-and-drop reordering.
  const onDragEnd = (result) => {
    if (!result.destination) return;
    const newCells = Array.from(cells);
    const [removed] = newCells.splice(result.source.index, 1);
    newCells.splice(result.destination.index, 0, removed);
    setCells(newCells);
    comm.send({ type: 'update_notebook', cells: newCells });
  };

  return (
    <div className="notebook-container max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">Interactive Notebook</h1>
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="notebook-cells">
          {(provided) => (
            <div {...provided.droppableProps} ref={provided.innerRef}>
              {cells.map((cell, index) => (
                <Draggable key={cell.id} draggableId={cell.id} index={index}>
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      className="notebook-cell bg-white rounded shadow p-4 mb-6 border"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center">
                          <span className="text-sm font-medium text-gray-600">
                            Cell {index + 1}
                          </span>
                          {cell.executed && (
                            <span title="Cell executed" className="ml-2 text-green-500">
                              ✔
                            </span>
                          )}
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            onClick={() => runCell(cell.id)}
                            disabled={cell.status === 'running'}
                            className="px-3 py-1 text-sm"
                          >
                            {cell.status === 'running' ? 'Running...' : 'Run'}
                          </Button>
                          <Button
                            variant="destructive"
                            onClick={() => deleteCell(cell.id)}
                            className="px-3 py-1 text-sm"
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                      <div className="mb-4">
                        {/* CodeMirror-based Python editor */}
                        <CodeMirror
                          value={cell.code}
                          height="auto"
                          theme={oneDark}
                          extensions={[python()]}
                          onChange={(value) => updateCellCode(cell.id, value)}
                        />
                      </div>
                      {(cell.status === 'running' || cell.status === 'error') && (
                        <div className="mt-2 text-sm text-gray-500">
                          {cell.status === 'error' ? 'Error occurred' : 'Executing cell...'}
                        </div>
                      )}
                      {cell.output && (
                        <div className="mt-4">
                          <HTMLRenderer
                            html={cell.output}
                            className="p-3 border rounded bg-gray-50 text-sm"
                          />
                        </div>
                      )}
                      {cell.error && (
                        <Alert variant="destructive" className="mt-4">
                          <span>{cell.error}</span>
                        </Alert>
                      )}
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
      <div className="flex justify-center">
        <Button onClick={addCell} className="px-6 py-2 text-lg">
          + Add Cell
        </Button>
      </div>
    </div>
  );
};

export default NotebookView;
