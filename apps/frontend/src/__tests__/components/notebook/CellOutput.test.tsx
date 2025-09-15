import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { CellOutput } from '../../../components/notebook/CellOutput';
import { CellType } from '@ai-jupyter/shared';

// Mock VisualizationOutput
jest.mock('../../../components/visualization/VisualizationOutput', () => ({
  VisualizationOutput: ({ data }: any) => (
    <div data-testid="visualization-output">
      Visualization: {JSON.stringify(data)}
    </div>
  )
}));

describe('CellOutput', () => {
  it('renders text output correctly', () => {
    const output = {
      outputType: 'text' as const,
      data: 'Hello, World!',
      metadata: { timestamp: '2023-01-01T00:00:00Z' }
    };

    render(<CellOutput output={output} cellType={CellType.CODE} />);

    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    expect(screen.getByText(/Output from/)).toBeInTheDocument();
  });

  it('renders HTML output correctly', () => {
    const output = {
      outputType: 'html' as const,
      data: '<p>HTML Content</p>',
      metadata: {}
    };

    render(<CellOutput output={output} cellType={CellType.CODE} />);

    expect(screen.getByText('HTML Content')).toBeInTheDocument();
  });

  it('renders image output correctly', () => {
    const output = {
      outputType: 'image' as const,
      data: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==',
      metadata: {}
    };

    render(<CellOutput output={output} cellType={CellType.CODE} />);

    const image = screen.getByAltText('Cell output');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', output.data);
  });

  it('renders visualization output correctly', () => {
    const visualizationData = {
      type: 'physics',
      positions: [[[0, 0, 0], [1, 1, 1]]],
      colors: [0xff0000, 0x00ff00]
    };

    const output = {
      outputType: 'visualization' as const,
      data: visualizationData,
      metadata: { source: 'physics_simulation' }
    };

    render(<CellOutput output={output} cellType={CellType.PHYSICS} />);

    expect(screen.getByTestId('visualization-output')).toBeInTheDocument();
    expect(screen.getByText(/Visualization:/)).toBeInTheDocument();
  });

  it('renders error text with error styling', () => {
    const output = {
      outputType: 'text' as const,
      data: 'Error: Something went wrong',
      metadata: { error: true }
    };

    render(<CellOutput output={output} cellType={CellType.CODE} />);

    const errorText = screen.getByText('Error: Something went wrong');
    expect(errorText).toBeInTheDocument();
    expect(errorText).toHaveClass('text-red-600', 'bg-red-50');
  });

  it('renders unknown output type with fallback message', () => {
    const output = {
      outputType: 'unknown' as any,
      data: 'Some data',
      metadata: {}
    };

    render(<CellOutput output={output} cellType={CellType.CODE} />);

    expect(screen.getByText('Unknown output type: unknown')).toBeInTheDocument();
  });

  it('renders without timestamp when not provided', () => {
    const output = {
      outputType: 'text' as const,
      data: 'Hello, World!',
      metadata: {}
    };

    render(<CellOutput output={output} cellType={CellType.CODE} />);

    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    expect(screen.queryByText(/Output from/)).not.toBeInTheDocument();
  });

  it('formats timestamp correctly', () => {
    const output = {
      outputType: 'text' as const,
      data: 'Hello, World!',
      metadata: { timestamp: '2023-01-01T12:30:45Z' }
    };

    render(<CellOutput output={output} cellType={CellType.CODE} />);

    // Should display formatted time
    expect(screen.getByText(/Output from/)).toBeInTheDocument();
  });

  it('passes metadata to visualization output', () => {
    const visualizationData = {
      type: 'plot',
      points: [[0, 0, 0], [1, 1, 1]]
    };

    const metadata = {
      source: 'test_simulation',
      timestamp: '2023-01-01T00:00:00Z'
    };

    const output = {
      outputType: 'visualization' as const,
      data: visualizationData,
      metadata
    };

    render(<CellOutput output={output} cellType={CellType.VISUALIZATION} />);

    expect(screen.getByTestId('visualization-output')).toBeInTheDocument();
    // The VisualizationOutput component should receive both data and metadata
  });

  it('handles different cell types correctly', () => {
    const output = {
      outputType: 'text' as const,
      data: 'Test output',
      metadata: {}
    };

    // Test with different cell types
    const { rerender } = render(<CellOutput output={output} cellType={CellType.CODE} />);
    expect(screen.getByText('Test output')).toBeInTheDocument();

    rerender(<CellOutput output={output} cellType={CellType.PHYSICS} />);
    expect(screen.getByText('Test output')).toBeInTheDocument();

    rerender(<CellOutput output={output} cellType={CellType.VISUALIZATION} />);
    expect(screen.getByText('Test output')).toBeInTheDocument();

    rerender(<CellOutput output={output} cellType={CellType.MARKDOWN} />);
    expect(screen.getByText('Test output')).toBeInTheDocument();
  });
});