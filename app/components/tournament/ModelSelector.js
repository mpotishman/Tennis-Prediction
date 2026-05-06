import React from 'react'

export default function ModelSelector({children, value, selectedModel, setSelectedModel}) {
  return (
    <div className="flex justify-center items-center m-4">
      <label className='flex gap-2 ui-text'>
          <input
            type="radio"
            name="model"
            checked={selectedModel === value}
            onChange={() => setSelectedModel(value)}
          />
          {children}
        </label>
    </div>
  )
}
