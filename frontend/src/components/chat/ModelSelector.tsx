interface ModelSelectorProps {
  selectedModel: 'openai' | 'anthropic';
  onModelChange: (model: 'openai' | 'anthropic') => void;
  disabled?: boolean;
}

const ModelSelector = ({ selectedModel, onModelChange, disabled = false }: ModelSelectorProps) => {
  const models = [
    {
      id: 'openai' as const,
      name: 'GPT-4 Turbo',
      provider: 'OpenAI',
      icon: '🤖',
      description: 'Advanced reasoning and function calling'
    },
    {
      id: 'anthropic' as const,
      name: 'Claude 3.5 Sonnet',
      provider: 'Anthropic',
      icon: '🧠',
      description: 'Thoughtful analysis and tool use'
    }
  ];

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        AI Model
      </label>
      <select
        value={selectedModel}
        onChange={(e) => onModelChange(e.target.value as 'openai' | 'anthropic')}
        disabled={disabled}
        className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {models.map((model) => (
          <option key={model.id} value={model.id}>
            {model.icon} {model.name} ({model.provider})
          </option>
        ))}
      </select>

      {/* Show description of selected model */}
      <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
        {models.find(m => m.id === selectedModel)?.description}
      </p>
    </div>
  );
};

export default ModelSelector;