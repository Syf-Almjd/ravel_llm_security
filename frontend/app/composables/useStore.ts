import { ref, computed } from 'vue'

const DEFAULT_SETTINGS = {
  theme: 'white',
  ollamaEndpoint: 'http://localhost:11434',
  selectedModel: 'gemma3:1b'
}

export const useStore = () => {
  const settings = useState<any>('settings', () => ({ ...DEFAULT_SETTINGS }))
  const conversations = useState<any[]>('conversations', () => [])
  const apiKeys = useState<any[]>('api_keys', () => [])
  const templates = useState<any[]>('templates', () => [])
  const config = useRuntimeConfig()
  const { authHeaders } = useAuth()

  // On client side, initialize from localStorage
  if (import.meta.client) {
    const savedSettings = localStorage.getItem('ravel_settings')
    if (savedSettings) {
      settings.value = { ...DEFAULT_SETTINGS, ...JSON.parse(savedSettings) }
    }
  }

  const updateSettings = (newSettings: any) => {
    settings.value = { ...settings.value, ...newSettings }
    if (import.meta.client) {
      localStorage.setItem('ravel_settings', JSON.stringify(settings.value))
    }
  }

  // API Keys
  const fetchApiKeys = async () => {
    try {
      // For mock keys as in phase 1 (or backend implementation if available)
      const savedKeys = localStorage.getItem('ravel_api_keys')
      if (savedKeys) {
        apiKeys.value = JSON.parse(savedKeys)
      } else {
        apiKeys.value = [
          { id: 'key_1', name: 'Production Agent API', key: 'rv_live_8f3d8a9e4b2c1d0f5e7a', createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), active: true },
          { id: 'key_2', name: 'Red Team Testing Key', key: 'rv_test_4c9b2e1a0f8d7e6c5b3a', createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), active: true }
        ]
        localStorage.setItem('ravel_api_keys', JSON.stringify(apiKeys.value))
      }
    } catch (err) {
      console.warn('Failed to load api keys:', err)
    }
  }

  const createApiKey = (name: string) => {
    const key = {
      id: 'key_' + Math.random().toString(36).substring(2, 9),
      name: name || 'Unnamed Key',
      key: 'rv_live_' + Array.from({ length: 20 }, () => Math.floor(Math.random() * 16).toString(16)).join(''),
      createdAt: new Date().toISOString(),
      active: true
    }
    apiKeys.value.unshift(key)
    if (import.meta.client) {
      localStorage.setItem('ravel_api_keys', JSON.stringify(apiKeys.value))
    }
    return key
  }

  const revokeApiKey = (id: string) => {
    apiKeys.value = apiKeys.value.filter(k => k.id !== id)
    if (import.meta.client) {
      localStorage.setItem('ravel_api_keys', JSON.stringify(apiKeys.value))
    }
  }

  // Templates
  const fetchTemplates = async () => {
    try {
      const data = await $fetch<any[]>(`${config.public.apiBase}/api/templates`, {
        headers: authHeaders()
      })
      templates.value = data
    } catch (err) {
      console.error('Failed to fetch templates:', err)
    }
  }

  // Conversations
  const fetchConversations = async () => {
    try {
      const data = await $fetch<any[]>(`${config.public.apiBase}/api/conversations`, {
        headers: authHeaders()
      })
      conversations.value = data
    } catch (err) {
      console.error('Failed to fetch conversations:', err)
    }
  }

  const sortedConversations = computed(() => {
    return [...conversations.value].sort((a, b) => {
      if (a.pinned && !b.pinned) return -1
      if (!a.pinned && b.pinned) return 1
      return new Date(b.updatedAt || b.createdAt).getTime() - new Date(a.updatedAt || a.createdAt).getTime()
    })
  })

  const getConversation = (id: string) => {
    return conversations.value.find(c => c.id === id)
  }

  const createConversation = async (title = 'New Security Session', templateId: string | null = null, category = 'General') => {
    try {
      const newConv = await $fetch<any>(`${config.public.apiBase}/api/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders()
        },
        body: { title, template_id: templateId, category }
      })
      conversations.value.unshift(newConv)
      return newConv
    } catch (err) {
      console.error('Failed to create conversation:', err)
      // Fallback
      const fallbackConv = {
        id: 'conv_' + Math.random().toString(36).substring(2, 9),
        title,
        template_id: templateId,
        category,
        pinned: false,
        createdAt: new Date().toISOString()
      }
      conversations.value.unshift(fallbackConv)
      return fallbackConv
    }
  }

  const deleteConversation = async (id: string) => {
    try {
      await $fetch(`${config.public.apiBase}/api/conversations/${id}`, {
        method: 'DELETE',
        headers: authHeaders()
      })
      conversations.value = conversations.value.filter(c => c.id !== id)
    } catch (err) {
      console.error('Failed to delete conversation:', err)
      conversations.value = conversations.value.filter(c => c.id !== id)
    }
  }

  const togglePinConversation = async (id: string) => {
    // Note: If no backend pin endpoint, toggle locally
    const conv = conversations.value.find(c => c.id === id)
    if (conv) {
      conv.pinned = !conv.pinned
      // We can also let it persist locally or trigger an API update if applicable.
    }
  }

  const updateConversationCategory = async (id: string, category: string) => {
    const conv = conversations.value.find(c => c.id === id)
    if (conv) {
      conv.category = category
    }
  }

  // Custom Dialog States
  const dialog = useState<any>('dialog', () => ({
    isOpen: false,
    title: '',
    message: '',
    type: 'alert',
    resolve: null
  }))

  const showAlert = (message: string, title = 'Notification') => {
    return new Promise<boolean>((resolve) => {
      dialog.value = {
        isOpen: true,
        title,
        message,
        type: 'alert',
        resolve: (val: boolean) => {
          dialog.value.isOpen = false
          resolve(val)
        }
      }
    })
  }

  const showConfirm = (message: string, title = 'Confirmation Required') => {
    return new Promise<boolean>((resolve) => {
      dialog.value = {
        isOpen: true,
        title,
        message,
        type: 'confirm',
        resolve: (val: boolean) => {
          dialog.value.isOpen = false
          resolve(val)
        }
      }
    })
  }

  return {
    settings,
    conversations,
    apiKeys,
    templates,
    updateSettings,
    fetchApiKeys,
    createApiKey,
    revokeApiKey,
    fetchTemplates,
    fetchConversations,
    sortedConversations,
    getConversation,
    createConversation,
    deleteConversation,
    togglePinConversation,
    updateConversationCategory,
    dialog,
    showAlert,
    showConfirm
  }
}
