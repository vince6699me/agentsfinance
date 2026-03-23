import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import AgentFinanceV3Dashboard from './AgentFinanceV3Dashboard.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AgentFinanceV3Dashboard />
  </StrictMode>,
)
