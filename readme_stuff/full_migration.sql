BEGIN;
--
-- Create model Edge
--
CREATE TABLE `studentGraph_edge` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `correctness` double precision NOT NULL, `visible` integer NOT NULL, `fixedValue` integer NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL);
--
-- Create model Node
--
CREATE TABLE `studentGraph_node` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `title` longtext NOT NULL, `nodePositionX` integer NOT NULL, `nodePositionY` integer NOT NULL, `correctness` double precision NOT NULL, `fixedValue` integer NOT NULL, `visible` integer NOT NULL, `alreadyCalculatedPos` integer NOT NULL, `customPos` integer NOT NULL, `dateAdded` datetime(6) NOT NULL, `linkedSolution` longtext NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL);
--
-- Create model Problem
--
CREATE TABLE `studentGraph_problem` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `graph` longtext NOT NULL, `isCalculatedPos` integer NOT NULL, `isCalculatingPos` integer NOT NULL, `multipleChoiceProblem` integer NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL);
--
-- Create model Resolution_history
--
CREATE TABLE `studentGraph_resolution_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `nodeIdList` longtext NOT NULL, `edgeIdList` longtext NOT NULL, `selectedOption` longtext NULL, `confirmationKey` longtext NOT NULL, `studentId` longtext NOT NULL, `correctness` double precision NOT NULL, `attempt` integer NOT NULL, `dateStarted` datetime(6) NOT NULL, `dateFinished` datetime(6) NULL, `dateModified` datetime(6) NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `problem_id` integer NOT NULL);
--
-- Create model Resolution
--
CREATE TABLE `studentGraph_resolution` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `nodeIdList` longtext NOT NULL, `edgeIdList` longtext NOT NULL, `selectedOption` longtext NULL, `confirmationKey` longtext NOT NULL, `studentId` longtext NOT NULL, `attempt` integer NOT NULL, `correctness` double precision NOT NULL, `dateStarted` datetime(6) NOT NULL, `dateFinished` datetime(6) NULL, `dateModified` datetime(6) NULL, `problem_id` integer NOT NULL);
--
-- Create model Node_votes_history
--
CREATE TABLE `studentGraph_node_votes_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `positiveCounter` integer NOT NULL, `negativeCounter` integer NOT NULL, `lastStudentId` longtext NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `node_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Node_votes
--
CREATE TABLE `studentGraph_node_votes` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `positiveCounter` integer NOT NULL, `negativeCounter` integer NOT NULL, `lastStudentId` longtext NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `node_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Node_history
--
CREATE TABLE `studentGraph_node_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `title` longtext NOT NULL, `nodePositionX` integer NOT NULL, `nodePositionY` integer NOT NULL, `correctness` double precision NOT NULL, `fixedValue` integer NOT NULL, `visible` integer NOT NULL, `alreadyCalculatedPos` integer NOT NULL, `customPos` integer NOT NULL, `dateAdded` datetime(6) NOT NULL, `linkedSolution` longtext NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `problem_id` integer NOT NULL);
--
-- Add field problem to node
--
ALTER TABLE `studentGraph_node` ADD COLUMN `problem_id` integer NOT NULL;
--
-- Create model KnowledgeComponent_history
--
CREATE TABLE `studentGraph_knowledgecomponent_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `edge_id` integer NULL, `node_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model KnowledgeComponent
--
CREATE TABLE `studentGraph_knowledgecomponent` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL, `edge_id` integer NULL, `node_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Hint_history
--
CREATE TABLE `studentGraph_hint_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `priority` integer NOT NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Hint
--
CREATE TABLE `studentGraph_hint` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `priority` integer NOT NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Explanation_history
--
CREATE TABLE `studentGraph_explanation_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `priority` integer NOT NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Explanation
--
CREATE TABLE `studentGraph_explanation` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `priority` integer NOT NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model ErrorSpecificFeedbacks_history
--
CREATE TABLE `studentGraph_errorspecificfeedbacks_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `priority` integer NOT NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model ErrorSpecificFeedbacks
--
CREATE TABLE `studentGraph_errorspecificfeedbacks` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `priority` integer NOT NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Edge_votes_history
--
CREATE TABLE `studentGraph_edge_votes_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `positiveCounter` integer NOT NULL, `negativeCounter` integer NOT NULL, `lastStudentId` longtext NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Edge_votes
--
CREATE TABLE `studentGraph_edge_votes` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `positiveCounter` integer NOT NULL, `negativeCounter` integer NOT NULL, `lastStudentId` longtext NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `edge_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Edge_history
--
CREATE TABLE `studentGraph_edge_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `correctness` double precision NOT NULL, `visible` integer NOT NULL, `fixedValue` integer NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `destNode_id` integer NOT NULL, `problem_id` integer NOT NULL, `sourceNode_id` integer NOT NULL);
--
-- Add field destNode to edge
--
ALTER TABLE `studentGraph_edge` ADD COLUMN `destNode_id` integer NOT NULL;
--
-- Add field problem to edge
--
ALTER TABLE `studentGraph_edge` ADD COLUMN `problem_id` integer NOT NULL;
--
-- Add field sourceNode to edge
--
ALTER TABLE `studentGraph_edge` ADD COLUMN `sourceNode_id` integer NOT NULL;
--
-- Create model Doubt_history
--
CREATE TABLE `studentGraph_doubt_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `type` integer NOT NULL, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `edge_id` integer NULL, `node_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Doubt
--
CREATE TABLE `studentGraph_doubt` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `type` integer NOT NULL, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `counter` integer NOT NULL, `edge_id` integer NULL, `node_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Attempt
--
CREATE TABLE `studentGraph_attempt` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `nodeIdList` longtext NOT NULL, `edgeIdList` longtext NOT NULL, `studentId` longtext NOT NULL, `attempt` integer NOT NULL, `dateCreated` datetime(6) NOT NULL, `problem_id` integer NOT NULL);
--
-- Create model AskedFeedback
--
CREATE TABLE `studentGraph_askedfeedback` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `feedbackType` longtext NOT NULL, `type` integer NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `doubt_id` integer NULL, `edge_id` integer NULL, `node_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Answer_history
--
CREATE TABLE `studentGraph_answer_history` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `originalId` integer NULL, `historyDate` datetime(6) NULL, `historyAction` longtext NULL, `doubt_id` integer NULL, `problem_id` integer NOT NULL);
--
-- Create model Answer
--
CREATE TABLE `studentGraph_answer` (`id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY, `text` longtext NOT NULL, `studentId` longtext NOT NULL, `dateAdded` datetime(6) NOT NULL, `dateModified` datetime(6) NULL, `usefulness` integer NOT NULL, `counter` integer NOT NULL, `doubt_id` integer NULL, `problem_id` integer NOT NULL);
ALTER TABLE `studentGraph_resolution_history` ADD CONSTRAINT `studentGraph_resolut_problem_id_7b3bf4d5_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_resolution` ADD CONSTRAINT `studentGraph_resolut_problem_id_6a33645e_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_node_votes_history` ADD CONSTRAINT `studentGraph_node_vo_node_id_5de8fac8_fk_studentGr` FOREIGN KEY (`node_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_node_votes_history` ADD CONSTRAINT `studentGraph_node_vo_problem_id_2f97318f_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_node_votes` ADD CONSTRAINT `studentGraph_node_votes_node_id_c0d4cab3_fk_studentGraph_node_id` FOREIGN KEY (`node_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_node_votes` ADD CONSTRAINT `studentGraph_node_vo_problem_id_52444837_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_node_history` ADD CONSTRAINT `studentGraph_node_hi_problem_id_bd51f25f_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_node` ADD CONSTRAINT `studentGraph_node_problem_id_8cf2bb51_fk_studentGraph_problem_id` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_knowledgecomponent_history` ADD CONSTRAINT `studentGraph_knowled_edge_id_2da76994_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_knowledgecomponent_history` ADD CONSTRAINT `studentGraph_knowled_node_id_066cb804_fk_studentGr` FOREIGN KEY (`node_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_knowledgecomponent_history` ADD CONSTRAINT `studentGraph_knowled_problem_id_d40a3369_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_knowledgecomponent` ADD CONSTRAINT `studentGraph_knowled_edge_id_4a46206c_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_knowledgecomponent` ADD CONSTRAINT `studentGraph_knowled_node_id_9c03d309_fk_studentGr` FOREIGN KEY (`node_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_knowledgecomponent` ADD CONSTRAINT `studentGraph_knowled_problem_id_a15f4e3d_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_hint_history` ADD CONSTRAINT `studentGraph_hint_hi_edge_id_0f933f40_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_hint_history` ADD CONSTRAINT `studentGraph_hint_hi_problem_id_e8e19c96_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_hint` ADD CONSTRAINT `studentGraph_hint_edge_id_ac0ee0e6_fk_studentGraph_edge_id` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_hint` ADD CONSTRAINT `studentGraph_hint_problem_id_eee61455_fk_studentGraph_problem_id` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_explanation_history` ADD CONSTRAINT `studentGraph_explana_edge_id_48c2da3f_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_explanation_history` ADD CONSTRAINT `studentGraph_explana_problem_id_85fa044b_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_explanation` ADD CONSTRAINT `studentGraph_explana_edge_id_5acc5da2_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_explanation` ADD CONSTRAINT `studentGraph_explana_problem_id_5265a513_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_errorspecificfeedbacks_history` ADD CONSTRAINT `studentGraph_errorsp_edge_id_abc56b65_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);ALTER TABLE `studentGraph_errorspecificfeedbacks_history` ADD CONSTRAINT `studentGraph_errorsp_problem_id_530373b8_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_errorspecificfeedbacks` ADD CONSTRAINT `studentGraph_errorsp_edge_id_cd06b18c_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_errorspecificfeedbacks` ADD CONSTRAINT `studentGraph_errorsp_problem_id_0cbf12ae_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_edge_votes_history` ADD CONSTRAINT `studentGraph_edge_vo_edge_id_03448c32_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_edge_votes_history` ADD CONSTRAINT `studentGraph_edge_vo_problem_id_65da823f_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_edge_votes` ADD CONSTRAINT `studentGraph_edge_votes_edge_id_e5f7ad7c_fk_studentGraph_edge_id` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_edge_votes` ADD CONSTRAINT `studentGraph_edge_vo_problem_id_ebe4cede_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_edge_history` ADD CONSTRAINT `studentGraph_edge_hi_destNode_id_ca027c94_fk_studentGr` FOREIGN KEY (`destNode_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_edge_history` ADD CONSTRAINT `studentGraph_edge_hi_problem_id_fab519db_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_edge_history` ADD CONSTRAINT `studentGraph_edge_hi_sourceNode_id_51b3fe96_fk_studentGr` FOREIGN KEY (`sourceNode_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_edge` ADD CONSTRAINT `studentGraph_edge_destNode_id_407b29cf_fk_studentGraph_node_id` FOREIGN KEY (`destNode_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_edge` ADD CONSTRAINT `studentGraph_edge_problem_id_c616ae02_fk_studentGraph_problem_id` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_edge` ADD CONSTRAINT `studentGraph_edge_sourceNode_id_eb93a96c_fk_studentGraph_node_id` FOREIGN KEY (`sourceNode_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_doubt_history` ADD CONSTRAINT `studentGraph_doubt_h_edge_id_ececf45b_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_doubt_history` ADD CONSTRAINT `studentGraph_doubt_h_node_id_65f1b490_fk_studentGr` FOREIGN KEY (`node_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_doubt_history` ADD CONSTRAINT `studentGraph_doubt_h_problem_id_a7d6aca7_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_doubt` ADD CONSTRAINT `studentGraph_doubt_edge_id_6685aac1_fk_studentGraph_edge_id` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_doubt` ADD CONSTRAINT `studentGraph_doubt_node_id_0426dd7d_fk_studentGraph_node_id` FOREIGN KEY (`node_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_doubt` ADD CONSTRAINT `studentGraph_doubt_problem_id_bd68cf8b_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_attempt` ADD CONSTRAINT `studentGraph_attempt_problem_id_b698d142_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_askedfeedback` ADD CONSTRAINT `studentGraph_askedfe_doubt_id_14ed25aa_fk_studentGr` FOREIGN KEY (`doubt_id`) REFERENCES `studentGraph_doubt` (`id`);
ALTER TABLE `studentGraph_askedfeedback` ADD CONSTRAINT `studentGraph_askedfe_edge_id_5035288d_fk_studentGr` FOREIGN KEY (`edge_id`) REFERENCES `studentGraph_edge` (`id`);
ALTER TABLE `studentGraph_askedfeedback` ADD CONSTRAINT `studentGraph_askedfe_node_id_10ed911f_fk_studentGr` FOREIGN KEY (`node_id`) REFERENCES `studentGraph_node` (`id`);
ALTER TABLE `studentGraph_askedfeedback` ADD CONSTRAINT `studentGraph_askedfe_problem_id_2d7e2fba_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_answer_history` ADD CONSTRAINT `studentGraph_answer__doubt_id_f5d889f7_fk_studentGr` FOREIGN KEY (`doubt_id`) REFERENCES `studentGraph_doubt` (`id`);
ALTER TABLE `studentGraph_answer_history` ADD CONSTRAINT `studentGraph_answer__problem_id_4fb92c63_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
ALTER TABLE `studentGraph_answer` ADD CONSTRAINT `studentGraph_answer_doubt_id_afa09054_fk_studentGraph_doubt_id` FOREIGN KEY (`doubt_id`) REFERENCES `studentGraph_doubt` (`id`);
ALTER TABLE `studentGraph_answer` ADD CONSTRAINT `studentGraph_answer_problem_id_4bc57aee_fk_studentGr` FOREIGN KEY (`problem_id`) REFERENCES `studentGraph_problem` (`id`);
COMMIT;