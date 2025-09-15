'use client';

import React from 'react';
import { AgentInfo } from '@ai-jupyter/shared';
import { useChatStore } from '../../stores/chatStore';

interface AgentSelectorProps {
  availableAgents: AgentInfo[];
  selectedAgents: string[];
  disabled?: boolean;
}

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  availableAgents,
  selectedAgents,
  disabled = false
}) => {
  const { toggleAgentSelection, setSelectedAgents } = useChatStore();

  const handleAgentToggle = (agentId: string) => {
    if (disabled) return;
    toggleAgentSelection(agentId);
  };

  const handleSelectAll = () => {
    if (disabled) return;
    const allAgentIds = availableAgents.map(agent => agent.id);
    setSelectedAgents(allAgentIds);
  };

  const handleSelectNone = () => {
    if (disabled) return;
    setSelectedAgents([]);
  };

  const getAgentIcon = (agentType: string) => {
    const icons: Record<string, string> = {
      physics: '⚛️',
      visualization: '📊',
      optimization: '⚡',
      debug: '🔧'
    };
    return icons[agentType] || '🤖';
  };

  return (
    <div className="agent-selector">
      <div className="agent-selector-header">
        <h4>Select AI Agents</h4>
        <div className="agent-selector-controls">
          <button
            className="select-button"
            onClick={handleSelectAll}
            disabled={disabled}
          >
            All
          </button>
          <button
            className="select-button"
            onClick={handleSelectNone}
            disabled={disabled}
          >
            None
          </button>
        </div>
      </div>
      
      <div className="agent-list">
        {availableAgents.map((agent) => (
          <div
            key={agent.id}
            className={`agent-item ${selectedAgents.includes(agent.id) ? 'selected' : ''} ${
              disabled ? 'disabled' : ''
            }`}
            onClick={() => handleAgentToggle(agent.id)}
          >
            <div className="agent-icon">
              {getAgentIcon(agent.type)}
            </div>
            
            <div className="agent-info">
              <div className="agent-name">{agent.name}</div>
              <div className="agent-description">{agent.description}</div>
              <div className="agent-capabilities">
                {agent.capabilities.map((capability) => (
                  <span key={capability} className="capability-tag">
                    {capability.replace('_', ' ')}
                  </span>
                ))}
              </div>
            </div>
            
            <div className="agent-status">
              <div className={`status-indicator ${agent.isAvailable ? 'available' : 'unavailable'}`}>
                {agent.isAvailable ? '✓' : '✗'}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {selectedAgents.length > 0 && (
        <div className="selected-agents-summary">
          <span className="summary-text">
            {selectedAgents.length} agent{selectedAgents.length !== 1 ? 's' : ''} selected
          </span>
          {selectedAgents.length > 1 && (
            <span className="coordination-note">
              Multiple agents will coordinate to answer your questions
            </span>
          )}
        </div>
      )}
    </div>
  );
};