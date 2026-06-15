# 📱 Mobile — Projeto Cidadão

> App mobile do Projeto Cidadão — fiscalização na palma da mão.

## 1. Visão Geral

App mobile multiplataforma (iOS + Android) do Projeto Cidadão. Permite:

- Navegar por **áreas temáticas** (saúde, educação, transporte, etc.)
- Acompanhar e fazer **cursos** de transparência
- Enviar e acompanhar **denúncias** (com foto, vídeo, geolocalização)
- Visualizar **denúncias no mapa** interativo
- Receber **alertas** do Farejador de Corrupção
- Acompanhar **gastos públicos** em tempo real
- Acompanhar seu **progresso** e **pontuação**

## 2. Stack Técnica

- **Framework:** React Native + Expo (SDK 50+)
- **Linguagem:** TypeScript
- **Navegação:** React Navigation v6
- **Estado:** Zustand ou Redux Toolkit
- **Requisições:** TanStack Query (React Query)
- **Mapas:** React Native Maps + Mapbox
- **UI:** NativeWind (Tailwind) ou Tamagui
- **Formulários:** React Hook Form + Zod
- **Storage:** Async Storage + Expo Secure Store
- **Notificações:** Expo Notifications + Telegram Bot
- **Animações:** Reanimated 3
- **Testes:** Jest + React Native Testing Library + Detox (E2E)
- **CI:** EAS Build (Expo Application Services)

## 3. Estrutura de Pastas

```
mobile/
├── src/
│   ├── app/                    # Entry point + App.tsx
│   ├── routes/                 # Rotas (React Navigation)
│   │   ├── auth.routes.tsx     # Rotas de autenticação
│   │   ├── app.routes.tsx      # Rotas autenticadas
│   │   └── index.tsx           # Root navigator
│   ├── screens/                # Telas
│   │   ├── auth/               # Login, cadastro, esqueci a senha
│   │   ├── home/               # Home (feed de áreas + denúncias)
│   │   ├── areas/              # Lista + detalhes de áreas
│   │   ├── cursos/             # Lista + detalhes de cursos
│   │   ├── denuncias/          # Lista, detalhes, criar denúncia
│   │   ├── mapa/               # Mapa de denúncias
│   │   ├── perfil/             # Perfil, pontos, conquistas
│   │   └── config/             # Configurações
│   ├── components/             # Componentes reutilizáveis
│   │   ├── ui/                 # Botões, inputs, cards, etc
│   │   ├── denuncia/           # Componentes de denúncia
│   │   ├── curso/              # Componentes de curso
│   │   └── mapa/               # Componentes de mapa
│   ├── hooks/                  # Hooks customizados
│   │   ├── useAuth.ts
│   │   ├── useAreas.ts
│   │   ├── useCursos.ts
│   │   ├── useDenuncias.ts
│   │   └── useFarejador.ts
│   ├── services/               # Integração com API
│   │   ├── api.ts              # Axios + interceptors
│   │   ├── auth.service.ts
│   │   ├── areas.service.ts
│   │   ├── cursos.service.ts
│   │   ├── denuncias.service.ts
│   │   └── farejador.service.ts
│   ├── stores/                 # Estado global (Zustand)
│   │   ├── auth.store.ts
│   │   ├── user.store.ts
│   │   └── notifications.store.ts
│   ├── utils/                  # Utilitários
│   │   ├── format.ts           # Formatação (moeda, data, etc)
│   │   ├── validation.ts       # Validação (Zod schemas)
│   │   └── permissions.ts      # Permissões (câmera, localização, etc)
│   ├── constants/              # Constantes
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── api.ts
│   ├── assets/                 # Imagens, ícones, fontes
│   └── types/                  # Tipos TypeScript compartilhados
├── app.json                    # Configuração do Expo
├── eas.json                     # Configuração do EAS Build
├── package.json
├── tsconfig.json
└── babel.config.js
```

## 4. Telas Principais

### 4.1. Home (Feed)
- Cards de áreas temáticas
- Denúncias recentes
- Alertas do Farejador
- Cursos em destaque

### 4.2. Áreas
- Lista de áreas com ícones
- Detalhes da área (descrição, cursos, denúncias)
- Estatísticas (gastos, denúncias, status)

### 4.3. Cursos
- Lista de cursos
- Detalhes do curso (descrição, módulos, fontes)
- Player de conteúdo (texto, vídeo, quiz)
- Acompanhamento de progresso

### 4.4. Denúncias
- Lista de denúncias (filtros: área, status, localização)
- Detalhes da denúncia (descrição, comentários, evidências)
- Criar denúncia (formulário + anexos + geolocalização)
- Acompanhar status

### 4.5. Mapa
- Mapa interativo com denúncias
- Filtros (categoria, status, período)
- Cluster de denúncias
- Detalhes ao tocar no pin

### 4.6. Perfil
- Dados do usuário
- Pontuação e conquistas
- Cursos concluídos
- Denúncias enviadas
- Configurações

## 5. Componentes-Chave

### 5.1. DenunciaCard
```tsx
type DenunciaCardProps = {
  denuncia: Denuncia
  onPress: () => void
}

export function DenunciaCard({ denuncia, onPress }: DenunciaCardProps) {
  return (
    <Pressable onPress={onPress} style={styles.card}>
      <Text style={styles.titulo}>{denuncia.titulo}</Text>
      <Text style={styles.categoria}>{denuncia.categoria}</Text>
      <Text style={styles.descricao} numberOfLines={3}>
        {denuncia.descricao}
      </Text>
      <View style={styles.footer}>
        <Text style={styles.status}>{denuncia.status}</Text>
        <Text style={styles.data}>{formatDate(denuncia.criadoEm)}</Text>
      </View>
    </Pressable>
  )
}
```

### 5.2. Mapa de Denúncias
```tsx
import MapView, { Marker } from 'react-native-maps'

export function MapaDenuncias({ denuncias }: Props) {
  return (
    <MapView
      style={{ flex: 1 }}
      initialRegion={{
        latitude: -15.7942,
        longitude: -47.8822,
        latitudeDelta: 0.0922,
        longitudeDelta: 0.0421,
      }}
    >
      {denuncias.map(d => (
        <Marker
          key={d.id}
          coordinate={{ latitude: d.lat, longitude: d.lng }}
          title={d.titulo}
          description={d.categoria}
        />
      ))}
    </MapView>
  )
}
```

### 5.3. Formulário de Denúncia
```tsx
export function FormDenuncia() {
  const { control, handleSubmit } = useForm<DenunciaInput>({
    resolver: zodResolver(denunciaSchema)
  })
  
  const onSubmit = async (data: DenunciaInput) => {
    await criarDenuncia(data)
  }
  
  return (
    <Form>
      <Controller name="titulo" control={control} render={...} />
      <Controller name="descricao" control={control} render={...} />
      <Controller name="categoria" control={control} render={...} />
      <Controller name="anexos" control={control} render={...} />
      <Button onPress={handleSubmit(onSubmit)}>Enviar Denúncia</Button>
    </Form>
  )
}
```

## 6. Permissões

- **Câmera** — fotos e vídeos de evidência
- **Localização** — georreferenciar denúncias
- **Notificações** — alertas do Farejador
- **Storage** — salvar anexos offline

## 7. Variáveis de Ambiente

```env
# .env
API_URL=http://localhost:3333
MAPBOX_TOKEN=changeme
EXPO_PUBLIC_TELEGRAM_BOT=projetocidadao_bot
SENTRY_DSN=changeme
```

## 8. Como Rodar Localmente

```bash
# 1. Instale o Expo CLI
npm install -g expo-cli

# 2. Instale as dependências
cd mobile
npm install

# 3. Inicie o servidor de desenvolvimento
npx expo start

# 4. Escaneie o QR Code com o app Expo Go (iOS/Android)
```

## 9. Build e Deploy

```bash
# Build para iOS e Android via EAS
eas build --platform all

# Submit para App Store e Google Play
eas submit --platform all
```

## 10. Roadmap

- [x] Especificação da stack e estrutura
- [ ] Configurar Expo + TypeScript
- [ ] Implementar autenticação
- [ ] Tela de áreas + cursos
- [ ] Tela de denúncias (lista, detalhes, criar)
- [ ] Mapa interativo
- [ ] Notificações push
- [ ] Integração com Telegram Bot
- [ ] Modo offline (denúncias salvas localmente)
- [ ] Testes E2E (Detox)
- [ ] Build e deploy (EAS)
- [ ] Publicação na App Store e Google Play

---

📌 *O mobile leva a fiscalização para a rua. Cidadãos com celular e dados viram fiscais do Estado — em tempo real, de qualquer lugar.*
