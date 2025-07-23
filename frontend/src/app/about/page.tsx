'use client';

import { MessageCircle, HelpCircle, FileQuestion, BookOpen, Brain, Zap, Users, Target } from 'lucide-react';

export default function AboutPage() {
  const features = [
    {
      icon: MessageCircle,
      title: "Chat",
      description: "Engage in intelligent conversations about your learning materials with our advanced AI assistant."
    },
    {
      icon: HelpCircle,
      title: "Q&A",
      description: "Get instant answers to your questions and deepen your understanding of complex topics."
    },
    {
      icon: FileQuestion,
      title: "Answer Quiz",
      description: "Test your knowledge with AI-generated quizzes tailored to your learning content."
    },
    {
      icon: BookOpen,
      title: "Notes",
      description: "Take, organize, and review your notes with intelligent suggestions and insights."
    }
  ];

  const steps = [
    {
      number: "01",
      title: "Select Your Book",
      description: "Choose from our extensive library or upload your own learning materials."
    },
    {
      number: "02",
      title: "Start Learning",
      description: "Engage with the content through chat, Q&A, quizzes, and note-taking."
    },
    {
      number: "03",
      title: "Track Progress",
      description: "Monitor your learning journey and receive personalized recommendations."
    }
  ];

  return (
    <div className="min-h-screen bg-background">
        {/* Hero Section */}
        <section className="relative py-20 px-6">
          <div className="max-w-6xl mx-auto text-center">
            <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-3xl -z-10" />
            <h1 className="text-5xl md:text-6xl font-bold text-text font-display mb-6">
              Welcome to{' '}
              <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                LuminaIQ-AI
              </span>
            </h1>
            <p className="text-xl text-text-secondary max-w-3xl mx-auto mb-8">
              Revolutionizing the way you learn with cutting-edge artificial intelligence. 
              Experience personalized, interactive, and efficient learning like never before.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <div className="flex items-center space-x-2 bg-card-bg px-4 py-2 rounded-full border border-border">
                <Brain className="h-5 w-5 text-primary" />
                <span className="text-text font-medium">AI-Powered</span>
              </div>
              <div className="flex items-center space-x-2 bg-card-bg px-4 py-2 rounded-full border border-border">
                <Zap className="h-5 w-5 text-secondary" />
                <span className="text-text font-medium">Interactive</span>
              </div>
              <div className="flex items-center space-x-2 bg-card-bg px-4 py-2 rounded-full border border-border">
                <Target className="h-5 w-5 text-accent" />
                <span className="text-text font-medium">Personalized</span>
              </div>
            </div>
          </div>
        </section>

        {/* Key Features Section */}
        <section className="py-20 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-text font-display mb-4">
                Powerful Features for Enhanced Learning
              </h2>
              <p className="text-lg text-text-secondary max-w-2xl mx-auto">
                Discover the comprehensive suite of tools designed to accelerate your learning journey
              </p>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <div key={index} className="bg-card-bg p-6 rounded-2xl border border-border hover:shadow-lg transition-all duration-300 group hover-scale stagger-item">
                  <div className="bg-primary/10 p-3 rounded-xl w-fit mb-4 group-hover:bg-primary/20 transition-colors">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold text-text mb-2">{feature.title}</h3>
                  <p className="text-text-secondary">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* How it Works Section */}
        <section className="py-20 px-6 bg-sidebar-bg">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-text font-display mb-4">
                How LuminaIQ-AI Works
              </h2>
              <p className="text-lg text-text-secondary max-w-2xl mx-auto">
                Get started with your personalized learning experience in just three simple steps
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-8">
              {steps.map((step, index) => (
                <div key={index} className="text-center">
                  <div className="bg-primary text-white text-2xl font-bold w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
                    {step.number}
                  </div>
                  <h3 className="text-xl font-semibold text-text mb-4">{step.title}</h3>
                  <p className="text-text-secondary">{step.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Technology Section */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-text font-display mb-6">
              Powered by Advanced AI Technology
            </h2>
            <p className="text-lg text-text-secondary mb-8">
              LuminaIQ-AI leverages state-of-the-art artificial intelligence to provide you with 
              intelligent insights, personalized recommendations, and adaptive learning experiences 
              that evolve with your progress.
            </p>
            <div className="bg-card-bg p-8 rounded-2xl border border-border">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <Brain className="h-8 w-8 text-primary" />
                <span className="text-2xl font-bold text-primary">Made with GENRECAI</span>
              </div>
              <p className="text-text-secondary">
                Built on cutting-edge generative AI technology for the most advanced learning experience
              </p>
            </div>
          </div>
        </section>
      </div>
  );
}
