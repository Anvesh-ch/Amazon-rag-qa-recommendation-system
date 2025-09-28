import React, { useState } from 'react';
import styled from 'styled-components';
import { Send, Loader, MessageSquare, ExternalLink, Star, Package } from 'lucide-react';
import { useMutation } from 'react-query';
import toast from 'react-hot-toast';
import { askQuestion } from '../services/api';

const QAContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const QuestionForm = styled.form`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
`;

const FormTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
`;

const InputGroup = styled.div`
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 120px;
  padding: ${props => props.theme.spacing.md};
  border: 2px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s ease;

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }

  &::placeholder {
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const ControlsRow = styled.div`
  display: flex;
  gap: ${props => props.theme.spacing.md};
  align-items: center;
  margin-bottom: ${props => props.theme.spacing.lg};

  @media (max-width: 640px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const SliderContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
`;

const SliderLabel = styled.label`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${props => props.theme.colors.text};
`;

const Slider = styled.input`
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: ${props => props.theme.colors.border};
  outline: none;
  -webkit-appearance: none;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    cursor: pointer;
  }

  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    cursor: pointer;
    border: none;
  }
`;

const SliderValue = styled.span`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
`;

const SubmitButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.xl};
  background: ${props => props.theme.colors.primary};
  color: white;
  border: none;
  border-radius: ${props => props.theme.borderRadius.md};
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 140px;
  justify-content: center;

  &:hover:not(:disabled) {
    background: ${props => props.theme.colors.primaryDark};
    transform: translateY(-1px);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const AnswerSection = styled.div`
  background: ${props => props.theme.colors.surface};
  border-radius: ${props => props.theme.borderRadius.lg};
  padding: ${props => props.theme.spacing.xl};
  margin-bottom: ${props => props.theme.spacing.xl};
  box-shadow: ${props => props.theme.shadows.md};
`;

const AnswerHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.md};
  margin-bottom: ${props => props.theme.spacing.lg};
`;

const AnswerTitle = styled.h3`
  font-size: 1.25rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
`;

const AnswerText = styled.div`
  font-size: 1rem;
  line-height: 1.7;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  white-space: pre-wrap;
`;

const SourcesSection = styled.div`
  margin-top: ${props => props.theme.spacing.xl};
`;

const SourcesTitle = styled.h4`
  font-size: 1.125rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin-bottom: ${props => props.theme.spacing.lg};
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
`;

const SourceCard = styled.div`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.lg};
  margin-bottom: ${props => props.theme.spacing.md};
  transition: all 0.2s ease;

  &:hover {
    border-color: ${props => props.theme.colors.primary};
    box-shadow: ${props => props.theme.shadows.sm};
  }
`;

const SourceHeader = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.sm};
  margin-bottom: ${props => props.theme.spacing.sm};
`;

const SourceTitle = styled.h5`
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  margin: 0;
  flex: 1;
`;

const SourceRating = styled.div`
  display: flex;
  align-items: center;
  gap: ${props => props.theme.spacing.xs};
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.875rem;
`;

const SourceCategory = styled.span`
  background: ${props => props.theme.colors.primary};
  color: white;
  padding: ${props => props.theme.spacing.xs} ${props => props.theme.spacing.sm};
  border-radius: ${props => props.theme.borderRadius.sm};
  font-size: 0.75rem;
  font-weight: 500;
`;

const SourceContent = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  line-height: 1.6;
  margin: 0;
`;

const MetricsContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: ${props => props.theme.spacing.md};
  margin-top: ${props => props.theme.spacing.lg};
`;

const MetricCard = styled.div`
  background: ${props => props.theme.colors.background};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: ${props => props.theme.spacing.lg};
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
  margin-bottom: ${props => props.theme.spacing.xs};
`;

const MetricLabel = styled.div`
  font-size: 0.875rem;
  color: ${props => props.theme.colors.textSecondary};
  font-weight: 500;
`;

const QATab = () => {
  const [question, setQuestion] = useState('');
  const [maxSources, setMaxSources] = useState(5);

  const askQuestionMutation = useMutation(askQuestion, {
    onSuccess: (data) => {
      toast.success('Answer generated successfully!');
    },
    onError: (error) => {
      toast.error('Failed to generate answer. Please try again.');
      console.error('Error:', error);
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!question.trim()) {
      toast.error('Please enter a question');
      return;
    }
    askQuestionMutation.mutate({ question, max_sources: maxSources });
  };

  const result = askQuestionMutation.data;

  return (
    <QAContainer>
      <QuestionForm onSubmit={handleSubmit}>
        <FormTitle>
          <MessageSquare size={24} />
          Ask Questions About Amazon Reviews
        </FormTitle>

        <InputGroup>
          <Label htmlFor="question">Your Question</Label>
          <TextArea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What do customers say about product quality? What are common complaints about this product?"
            disabled={askQuestionMutation.isLoading}
          />
        </InputGroup>

        <ControlsRow>
          <SliderContainer>
            <SliderLabel>Max Sources: {maxSources}</SliderLabel>
            <Slider
              type="range"
              min="1"
              max="20"
              value={maxSources}
              onChange={(e) => setMaxSources(parseInt(e.target.value))}
              disabled={askQuestionMutation.isLoading}
            />
            <SliderValue>1-20 sources</SliderValue>
          </SliderContainer>

          <SubmitButton type="submit" disabled={askQuestionMutation.isLoading}>
            {askQuestionMutation.isLoading ? (
              <Loader size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
            {askQuestionMutation.isLoading ? 'Generating...' : 'Ask Question'}
          </SubmitButton>
        </ControlsRow>
      </QuestionForm>

      {result && (
        <AnswerSection>
          <AnswerHeader>
            <AnswerTitle>🤖 AI Answer</AnswerTitle>
          </AnswerHeader>

          <AnswerText>{result.answer}</AnswerText>

          {result.sources && result.sources.length > 0 && (
            <SourcesSection>
              <SourcesTitle>
                📚 Sources ({result.num_sources})
              </SourcesTitle>

              {result.sources.map((source, index) => (
                <SourceCard key={index}>
                  <SourceHeader>
                    <SourceTitle>{source.metadata?.product_title || 'Unknown Product'}</SourceTitle>
                    <SourceRating>
                      <Star size={16} />
                      {source.metadata?.star_rating || 'N/A'}/5
                    </SourceRating>
                    <SourceCategory>{source.metadata?.category || 'Unknown'}</SourceCategory>
                  </SourceHeader>
                  <SourceContent>{source.content}</SourceContent>
                </SourceCard>
              ))}
            </SourcesSection>
          )}

          <MetricsContainer>
            <MetricCard>
              <MetricValue>{result.num_sources}</MetricValue>
              <MetricLabel>Sources Found</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>{result.answer?.length || 0}</MetricValue>
              <MetricLabel>Answer Length</MetricLabel>
            </MetricCard>
            <MetricCard>
              <MetricValue>~2-5s</MetricValue>
              <MetricLabel>Processing Time</MetricLabel>
            </MetricCard>
          </MetricsContainer>
        </AnswerSection>
      )}
    </QAContainer>
  );
};

export default QATab;
