/**
 * Backward-compatible re-export from the multi-provider LLM service.
 *
 * New code should import from '@/services/llm' directly.
 */
import { createChatCompletion } from './llm';

export { createChatCompletion };
